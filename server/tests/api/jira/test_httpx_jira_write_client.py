from collections.abc import AsyncIterator

import httpx
import pytest
from pydantic import JsonValue

from app.modules.jira import (
    JiraAttachment,
    JiraDocumentBlock,
    JiraDocumentBlockKind,
    JiraInvalidCredentialsError,
    JiraIssueRejectedError,
    JiraNewIssue,
    JiraPermission,
    JiraUnreachableError,
    JiraWriteNotAllowedError,
)
from app.modules.jira.infrastructure import HttpxJiraClient
from tests.api.jira.test_httpx_jira_client import (
    CREDENTIALS,
    SITE_URL,
    RecordingSleep,
    ScriptedJira,
    json_response,
    read_json_body,
)

NEW_ISSUE = JiraNewIssue(
    jira_project_key="PAY",
    issue_type_name="Bug",
    summary="TC-4 Pay by card: step 2 failed",
    description=[JiraDocumentBlock(kind=JiraDocumentBlockKind.PARAGRAPH, texts=["The payment failed."])],
)


@pytest.fixture
def scripted_jira() -> ScriptedJira:
    return ScriptedJira()


@pytest.fixture
def recording_sleep() -> RecordingSleep:
    return RecordingSleep()


@pytest.fixture
async def jira_client(scripted_jira: ScriptedJira, recording_sleep: RecordingSleep) -> AsyncIterator[HttpxJiraClient]:
    async with httpx.AsyncClient(transport=httpx.MockTransport(scripted_jira.handle)) as http_client:
        yield HttpxJiraClient(http_client, recording_sleep)


async def test_create_issue_sends_the_fields_with_an_adf_description(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [json_response({"id": "10042", "key": "PAY-42", "self": "x"}, status_code=201)]

    created = await jira_client.create_issue(CREDENTIALS, NEW_ISSUE)

    request = scripted_jira.requests[0]
    assert request.method == "POST"
    assert str(request.url) == f"{SITE_URL}/rest/api/3/issue"
    assert read_json_body(request) == {
        "fields": {
            "project": {"key": "PAY"},
            "issuetype": {"name": "Bug"},
            "summary": "TC-4 Pay by card: step 2 failed",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The payment failed."}]}],
            },
        }
    }
    assert created.key == "PAY-42"
    assert created.id == "10042"
    assert created.url == f"{SITE_URL}/browse/PAY-42"


async def test_a_forbidden_write_means_the_account_cannot_write(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [httpx.Response(403), httpx.Response(403)]

    with pytest.raises(JiraWriteNotAllowedError):
        await jira_client.create_issue(CREDENTIALS, NEW_ISSUE)
    with pytest.raises(JiraWriteNotAllowedError):
        await jira_client.add_comment(CREDENTIALS, "PAY-1", NEW_ISSUE.description)


async def test_an_unauthorized_write_means_invalid_credentials(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [httpx.Response(401)]

    with pytest.raises(JiraInvalidCredentialsError):
        await jira_client.create_issue(CREDENTIALS, NEW_ISSUE)


async def test_a_refused_issue_type_is_reported_as_rejected(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [json_response({"errors": {"issuetype": "invalid"}}, status_code=400)]

    with pytest.raises(JiraIssueRejectedError):
        await jira_client.create_issue(CREDENTIALS, NEW_ISSUE)


async def test_writes_retry_after_a_rate_limit(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira, recording_sleep: RecordingSleep
) -> None:
    scripted_jira.responses = [
        httpx.Response(429, headers={"Retry-After": "2"}),
        json_response({"id": "1", "key": "PAY-1"}, status_code=201),
    ]

    created = await jira_client.create_issue(CREDENTIALS, NEW_ISSUE)

    assert created.key == "PAY-1"
    assert recording_sleep.delays == [2.0]
    assert len(scripted_jira.requests) == 2


async def test_a_write_still_rate_limited_after_the_retries_is_unreachable(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [httpx.Response(429) for _ in range(4)]

    with pytest.raises(JiraUnreachableError):
        await jira_client.add_comment(CREDENTIALS, "PAY-1", NEW_ISSUE.description)


async def test_an_attachment_is_sent_as_multipart_with_the_no_check_header(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [json_response([{"id": "1"}])]

    await jira_client.add_attachment(
        CREDENTIALS,
        "PAY-42",
        JiraAttachment(file_name="step-2.png", content_type="image/png", content=b"\x89PNG-bytes"),
    )

    request = scripted_jira.requests[0]
    assert request.method == "POST"
    assert str(request.url) == f"{SITE_URL}/rest/api/3/issue/PAY-42/attachments"
    assert request.headers["X-Atlassian-Token"] == "no-check"
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b'name="file"; filename="step-2.png"' in request.content
    assert b"\x89PNG-bytes" in request.content


async def test_a_comment_is_posted_as_an_adf_body(jira_client: HttpxJiraClient, scripted_jira: ScriptedJira) -> None:
    scripted_jira.responses = [json_response({"id": "5"}, status_code=201)]

    await jira_client.add_comment(CREDENTIALS, "PAY-7", NEW_ISSUE.description)

    request = scripted_jira.requests[0]
    assert str(request.url) == f"{SITE_URL}/rest/api/3/issue/PAY-7/comment"
    assert "X-Atlassian-Token" not in request.headers
    assert read_json_body(request) == {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The payment failed."}]}],
        }
    }


async def test_issues_are_linked_with_relates_to(jira_client: HttpxJiraClient, scripted_jira: ScriptedJira) -> None:
    scripted_jira.responses = [httpx.Response(201)]

    await jira_client.link_issues(CREDENTIALS, "PAY-42", "PAY-7")

    request = scripted_jira.requests[0]
    assert str(request.url) == f"{SITE_URL}/rest/api/3/issueLink"
    assert read_json_body(request) == {
        "type": {"name": "Relates"},
        "inwardIssue": {"key": "PAY-42"},
        "outwardIssue": {"key": "PAY-7"},
    }


async def test_my_permissions_lists_the_missing_write_permissions_for_a_project(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [
        json_response(
            {
                "permissions": {
                    "CREATE_ISSUES": {"key": "CREATE_ISSUES", "havePermission": True},
                    "ADD_COMMENTS": {"key": "ADD_COMMENTS", "havePermission": False},
                    "CREATE_ATTACHMENTS": {"key": "CREATE_ATTACHMENTS", "havePermission": True},
                }
            }
        )
    ]

    missing = await jira_client.list_missing_permissions(CREDENTIALS, "PAY")

    request = scripted_jira.requests[0]
    assert request.method == "GET"
    assert request.url.path == "/rest/api/3/mypermissions"
    assert request.url.params["projectKey"] == "PAY"
    assert request.url.params["permissions"] == "CREATE_ISSUES,ADD_COMMENTS,CREATE_ATTACHMENTS,LINK_ISSUES"
    assert missing == frozenset({JiraPermission.ADD_COMMENTS, JiraPermission.LINK_ISSUES})


async def test_my_permissions_without_a_project_and_an_unknown_project(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    all_granted: dict[str, JsonValue] = {permission.value: {"havePermission": True} for permission in JiraPermission}
    scripted_jira.responses = [json_response({"permissions": all_granted}), httpx.Response(404)]

    assert await jira_client.list_missing_permissions(CREDENTIALS, None) == frozenset()
    assert "projectKey" not in scripted_jira.requests[0].url.params
    assert await jira_client.list_missing_permissions(CREDENTIALS, "GONE") == frozenset(JiraPermission)


def build_status_issue(key: str, status_name: str, category_key: str) -> JsonValue:
    return {"key": key, "fields": {"status": {"name": status_name, "statusCategory": {"key": category_key}}}}


async def test_issue_statuses_come_from_one_jql_search_per_hundred_keys(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    keys = [f"PAY-{number}" for number in range(1, 151)]
    scripted_jira.responses = [
        json_response(
            {
                "issues": [
                    build_status_issue("PAY-1", "Done", "done"),
                    build_status_issue("PAY-10", "In Progress", "indeterminate"),
                ]
            }
        ),
        json_response({"issues": [build_status_issue("PAY-99", "To Do", "new")]}),
    ]

    statuses = await jira_client.list_issue_statuses(CREDENTIALS, [*keys, "PAY-1", 'BAD") OR key = "X'])

    assert len(scripted_jira.requests) == 2
    first_body = read_json_body(scripted_jira.requests[0])
    assert isinstance(first_body, dict)
    assert first_body["fields"] == ["status"]
    jql = first_body["jql"]
    assert isinstance(jql, str)
    assert jql.startswith('key in ("PAY-1", "PAY-10", "PAY-100"')
    assert "BAD" not in jql
    assert [(status.key, status.status_name, status.is_done) for status in statuses] == [
        ("PAY-1", "Done", True),
        ("PAY-10", "In Progress", False),
        ("PAY-99", "To Do", False),
    ]


async def test_a_refused_status_search_returns_nothing(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [json_response({"errorMessages": ["An issue with key 'PAY-1' does not exist"]}, 400)]

    assert await jira_client.list_issue_statuses(CREDENTIALS, ["PAY-1"]) == []
