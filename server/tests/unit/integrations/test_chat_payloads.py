from uuid import uuid4

import pytest

from app.modules.integrations.domains.chat_message.entity import ChatFact, ChatMessage
from app.modules.integrations.domains.chat_project.entity import ChatProject
from app.modules.integrations.domains.chat_run_details.entity import ChatRunDetails
from app.modules.integrations.typing.enums import ChatChannelKind, IntegrationEvent
from app.modules.integrations.utils.chat_message import build_run_message
from app.modules.integrations.utils.chat_payload import build_chat_payload
from app.modules.integrations.utils.slack_payload import shorten_slack_text

MESSAGE = ChatMessage(
    title="Run failed on SHOP-12",
    text="Pay with <saved> card & coupon",
    facts=[ChatFact(label="Passed", value="8"), ChatFact(label="Failed", value="1")],
    link_url="https://tessio.test/projects/SHOP/runs/42",
    footer="Tessio · Shop",
)


def test_slack_gets_block_kit_with_a_fallback_text_and_a_button() -> None:
    payload = build_chat_payload(ChatChannelKind.SLACK, MESSAGE)

    assert payload == {
        "text": "Run failed on SHOP-12",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "Run failed on SHOP-12"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": "Pay with &lt;saved&gt; card &amp; coupon"}},
            {
                "type": "section",
                "fields": [{"type": "mrkdwn", "text": "*Passed*\n8"}, {"type": "mrkdwn", "text": "*Failed*\n1"}],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Open in Tessio"},
                        "url": "https://tessio.test/projects/SHOP/runs/42",
                    }
                ],
            },
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "Tessio · Shop"}]},
        ],
    }


def test_slack_header_is_cut_to_the_block_kit_limit() -> None:
    payload = build_chat_payload(ChatChannelKind.SLACK, MESSAGE.model_copy(update={"title": "x" * 400}))

    blocks = payload["blocks"]
    assert isinstance(blocks, list)
    header = blocks[0]
    assert isinstance(header, dict)
    header_text = header["text"]
    assert isinstance(header_text, dict)
    assert header_text["text"] == "x" * 149 + "…"


def test_slack_escapes_the_fallback_text() -> None:
    payload = build_chat_payload(ChatChannelKind.SLACK, MESSAGE.model_copy(update={"title": "Fix <b> & ship"}))

    assert payload["text"] == "Fix &lt;b&gt; &amp; ship"


def test_slack_cuts_text_without_splitting_an_escaped_character() -> None:
    assert shorten_slack_text("ab&cd", 6) == "ab…"
    assert shorten_slack_text("ab&cd", 8) == "ab&amp;…"
    assert shorten_slack_text("ab&cd", 9) == "ab&amp;cd"
    assert len(shorten_slack_text("&" * 4000, 3000)) <= 3000


def test_slack_leaves_out_empty_sections() -> None:
    payload = build_chat_payload(ChatChannelKind.SLACK, MESSAGE.model_copy(update={"text": None, "facts": []}))

    blocks = payload["blocks"]
    assert isinstance(blocks, list)
    assert [block["type"] for block in blocks if isinstance(block, dict)] == ["header", "actions", "context"]


def test_teams_gets_an_adaptive_card_in_the_workflows_message_format() -> None:
    payload = build_chat_payload(ChatChannelKind.TEAMS, MESSAGE)

    assert payload == {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "Run failed on SHOP-12",
                            "weight": "Bolder",
                            "size": "Medium",
                            "wrap": True,
                        },
                        {"type": "TextBlock", "text": "Pay with <saved> card & coupon", "wrap": True},
                        {
                            "type": "FactSet",
                            "facts": [{"title": "Passed", "value": "8"}, {"title": "Failed", "value": "1"}],
                        },
                        {"type": "TextBlock", "text": "Tessio · Shop", "isSubtle": True, "size": "Small", "wrap": True},
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "Open in Tessio",
                            "url": "https://tessio.test/projects/SHOP/runs/42",
                        }
                    ],
                },
            }
        ],
    }


def build_run_details(story_jira_key: str | None, story_title: str | None, suite_name: str | None) -> ChatRunDetails:
    return ChatRunDetails(
        id=uuid4(),
        status="passed",
        executor="ci",
        environment_name="Staging",
        started_by_name="Ana",
        story_jira_key=story_jira_key,
        story_title=story_title,
        suite_name=suite_name,
        passed_count=8,
        failed_count=0,
        blocked_count=None,
        skipped_count=1,
    )


@pytest.mark.parametrize(
    ("story_jira_key", "story_title", "suite_name", "started_title", "finished_title"),
    [
        ("SHOP-12", "Pay with a saved card", None, "Run started on SHOP-12", "Run passed on SHOP-12"),
        (None, None, "Checkout", "Suite run started: Checkout", "Suite run passed: Checkout"),
        (None, None, None, "CI run started · Staging", "CI run passed · Staging"),
    ],
)
def test_a_run_title_names_its_suite_its_story_or_its_environment(
    story_jira_key: str | None, story_title: str | None, suite_name: str | None, started_title: str, finished_title: str
) -> None:
    run = build_run_details(story_jira_key, story_title, suite_name)
    project = ChatProject(id=uuid4(), key="SHOP", name="Shop")

    started = build_run_message(IntegrationEvent.RUN_STARTED, run, project, "https://tessio.test")
    finished = build_run_message(IntegrationEvent.RUN_FINISHED, run, project, "https://tessio.test")

    assert started.title == started_title
    assert finished.title == finished_title
    assert started.text == story_title
    for message in (started, finished):
        shown_texts = [message.title, message.text or "", *(fact.value for fact in message.facts)]
        assert all("None" not in shown_text for shown_text in shown_texts)
    assert [(fact.label, fact.value) for fact in finished.facts] == [
        ("Passed", "8"),
        ("Failed", "0"),
        ("Skipped", "1"),
        ("Executor", "CI"),
        ("Environment", "Staging"),
    ]
