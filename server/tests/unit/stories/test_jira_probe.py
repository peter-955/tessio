import argparse
import json
from datetime import UTC, datetime

import pytest

from app.commands import jira_probe
from app.commands.jira_probe import build_probe_report, parse_issue_key, probe_issue
from app.modules.jira import JiraIssue, JiraUnreachableError
from tests.unit.stories.adf_fixtures import load_adf_fixture


def build_issue(issue_type_name: str = "Story") -> JiraIssue:
    return JiraIssue(
        id="10001",
        key="SHOP-12",
        summary="Pay by card",
        description=load_adf_fixture("heading_bullet_list"),
        status_name="In Progress",
        issue_type_name=issue_type_name,
        is_subtask=False,
        updated_at=datetime(2026, 10, 30, tzinfo=UTC),
    )


def test_the_report_lists_the_parsed_criteria_and_node_types() -> None:
    report = build_probe_report(build_issue(), is_including_description=False)

    assert report == {
        "key": "SHOP-12",
        "issueType": "Story",
        "isSubtask": False,
        "isEpic": False,
        "status": "In Progress",
        "summary": "Pay by card",
        "criteriaSource": "marked_list",
        "criteria": [
            {"code": "AC1", "text": "Card payment succeeds"},
            {"code": "AC2", "text": "Declined card shows an error"},
        ],
        "nodeTypes": ["bulletList", "doc", "heading", "listItem", "paragraph", "text"],
    }


def test_the_raw_flag_adds_the_description() -> None:
    issue = build_issue("Epic")

    report = build_probe_report(issue, is_including_description=True)

    assert report["isEpic"] is True
    assert report["description"] == issue.description


@pytest.mark.parametrize("issue_key", ["SHOP-1", "AB_2-345"])
def test_valid_issue_keys_are_accepted(issue_key: str) -> None:
    assert parse_issue_key(issue_key) == issue_key


@pytest.mark.parametrize("issue_key", ["shop-1", "S-1", "SHOP", "SHOP-1 OR 1=1", 'SHOP-1"'])
def test_invalid_issue_keys_are_refused(issue_key: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        parse_issue_key(issue_key)


async def test_the_probe_prints_the_report_as_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def fetch_issue(issue_key: str) -> JiraIssue | None:
        return build_issue()

    monkeypatch.setattr(jira_probe, "fetch_issue", fetch_issue)

    exit_code = await probe_issue("SHOP-12", is_including_description=False)

    output = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(output.out)["criteriaSource"] == "marked_list"
    assert output.err == ""


async def test_the_probe_reports_a_missing_issue(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def fetch_issue(issue_key: str) -> JiraIssue | None:
        return None

    monkeypatch.setattr(jira_probe, "fetch_issue", fetch_issue)

    exit_code = await probe_issue("SHOP-404", is_including_description=False)

    output = capsys.readouterr()
    assert exit_code == 1
    assert output.out == ""
    assert output.err == "NOT_FOUND: Jira issue SHOP-404 not found.\n"


async def test_the_probe_reports_a_jira_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def fetch_issue(issue_key: str) -> JiraIssue | None:
        raise JiraUnreachableError

    monkeypatch.setattr(jira_probe, "fetch_issue", fetch_issue)

    exit_code = await probe_issue("SHOP-12", is_including_description=True)

    assert exit_code == 1
    assert capsys.readouterr().err == "JIRA_UNREACHABLE: Jira could not be reached. Try again later.\n"
