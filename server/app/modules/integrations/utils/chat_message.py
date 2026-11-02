from urllib.parse import quote

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.domains.chat_failure_details.entity import ChatFailureDetails
from app.modules.integrations.domains.chat_gap_details.entity import ChatGapDetails
from app.modules.integrations.domains.chat_message.entity import ChatFact, ChatMessage
from app.modules.integrations.domains.chat_plan_details.entity import ChatPlanDetails
from app.modules.integrations.domains.chat_project.entity import ChatProject
from app.modules.integrations.domains.chat_run_details.entity import ChatRunDetails
from app.modules.integrations.domains.chat_story_details.entity import ChatStoryDetails
from app.modules.integrations.typing.constants import (
    CHAT_EMPTY_VALUE,
    CHAT_EVENT_LABELS,
    CHAT_FOOTER_TEMPLATE,
    CHAT_MESSAGE_TEXT_LIMIT,
    CHAT_TEST_EVENTS_LABEL,
    CHAT_TEST_MESSAGE_TEXT,
    CHAT_TEST_MESSAGE_TITLE,
    CHAT_TITLE_LIMIT,
)
from app.modules.integrations.typing.enums import IntegrationEvent
from app.modules.integrations.utils.chat_text import humanize_value, label_executor, shorten_chat_text


def build_project_url(client_url: str, project: ChatProject) -> str:
    return f"{client_url.rstrip('/')}/projects/{quote(project.key, safe='')}"


def build_message(
    project: ChatProject, title: str, text: str | None, facts: list[ChatFact], link_url: str
) -> ChatMessage:
    return ChatMessage(
        title=shorten_chat_text(title, CHAT_TITLE_LIMIT),
        text=None if not text else shorten_chat_text(text, CHAT_MESSAGE_TEXT_LIMIT),
        facts=facts,
        link_url=link_url,
        footer=CHAT_FOOTER_TEMPLATE.format(project_name=project.name),
    )


def build_run_message(
    event: IntegrationEvent, run: ChatRunDetails, project: ChatProject, client_url: str
) -> ChatMessage:
    link_url = f"{build_project_url(client_url, project)}/runs/{run.id}"
    facts = [ChatFact(label="Executor", value=label_executor(run.executor))]
    facts.append(ChatFact(label="Environment", value=run.environment_name))
    if event is IntegrationEvent.RUN_STARTED:
        facts.append(ChatFact(label="Started by", value=run.started_by_name))
        title = build_run_title(run, "started")
    else:
        facts = build_run_count_facts(run) + facts
        title = build_run_title(run, run.status)
    return build_message(project, title, run.story_title, facts, link_url)


def build_run_title(run: ChatRunDetails, outcome: str) -> str:
    if run.suite_name is not None:
        return f"Suite run {outcome}: {run.suite_name}"
    if run.story_jira_key is not None:
        return f"Run {outcome} on {run.story_jira_key}"
    return f"{label_executor(run.executor)} run {outcome} · {run.environment_name}"


def build_run_count_facts(run: ChatRunDetails) -> list[ChatFact]:
    counts = [
        ("Passed", run.passed_count),
        ("Failed", run.failed_count),
        ("Blocked", run.blocked_count),
        ("Skipped", run.skipped_count),
    ]
    return [ChatFact(label=label, value=str(count)) for label, count in counts if count is not None]


def build_failure_message(
    event: IntegrationEvent, failure: ChatFailureDetails, project: ChatProject, client_url: str
) -> ChatMessage:
    link_url = f"{build_project_url(client_url, project)}/failures/{failure.id}"
    assignee_fact = ChatFact(label="Assignee", value=failure.assignee_name or CHAT_EMPTY_VALUE)
    if event is IntegrationEvent.FAILURE_OPENED:
        return build_message(
            project,
            f"Failure opened on {failure.story_jira_key}",
            f"{failure.test_case_code} · {failure.test_case_title}",
            [ChatFact(label="Status", value=humanize_value(failure.status)), assignee_fact],
            link_url,
        )
    return build_message(
        project,
        f"Failure {failure.test_case_code} is now {humanize_value(failure.status).lower()}",
        failure.test_case_title,
        [ChatFact(label="Story", value=failure.story_jira_key), assignee_fact],
        link_url,
    )


def build_gap_message(gap: ChatGapDetails, project: ChatProject, client_url: str) -> ChatMessage:
    link_url = f"{build_project_url(client_url, project)}/stories/{quote(gap.story_jira_key, safe='')}?tab=gaps"
    assignee = gap.assignee_name or (None if gap.assignee_role is None else gap.assignee_role.upper())
    return build_message(
        project,
        f"Gap raised on {gap.story_jira_key}",
        gap.question,
        [
            ChatFact(label="Severity", value=humanize_value(gap.severity)),
            ChatFact(label="Assigned to", value=assignee or CHAT_EMPTY_VALUE),
            ChatFact(label="Raised by", value=gap.raised_by_name),
        ],
        link_url,
    )


def build_story_message(story: ChatStoryDetails, project: ChatProject, client_url: str) -> ChatMessage:
    link_url = f"{build_project_url(client_url, project)}/stories/{quote(story.jira_key, safe='')}"
    return build_message(
        project,
        f"Story signed off: {story.jira_key}",
        story.title,
        [ChatFact(label="Signed off by", value=story.signed_off_by_name or CHAT_EMPTY_VALUE)],
        link_url,
    )


def build_plan_message(plan: ChatPlanDetails, project: ChatProject, client_url: str) -> ChatMessage:
    link_url = f"{build_project_url(client_url, project)}/plans/{plan.id}"
    facts = [ChatFact(label="Signed off by", value=plan.signed_off_by_name or CHAT_EMPTY_VALUE)]
    if plan.target_date is not None:
        facts.append(ChatFact(label="Target date", value=plan.target_date.isoformat()))
    return build_message(project, f"Plan signed off: {plan.name}", None, facts, link_url)


def build_test_message(chat_channel: ChatChannel, project: ChatProject, client_url: str) -> ChatMessage:
    event_labels = ", ".join(CHAT_EVENT_LABELS[event] for event in chat_channel.events)
    return build_message(
        project,
        CHAT_TEST_MESSAGE_TITLE,
        CHAT_TEST_MESSAGE_TEXT.format(project_name=project.name, project_key=project.key),
        [ChatFact(label=CHAT_TEST_EVENTS_LABEL, value=event_labels or CHAT_EMPTY_VALUE)],
        f"{build_project_url(client_url, project)}/settings",
    )
