import base64
import json
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import httpx
import pytest
from pydantic import JsonValue, SecretStr

from app.modules.jira import (
    JiraCredentials,
    JiraInvalidCredentialsError,
    JiraSprintState,
    JiraUnreachableError,
)
from app.modules.jira.errors import JiraProjectNotFoundError
from app.modules.jira.infrastructure import HttpxJiraClient

SITE_URL = "https://team.atlassian.net"
CREDENTIALS = JiraCredentials(
    site_url=SITE_URL, account_email="bot@tessio.test", api_token=SecretStr("secret-jira-token")
)

ResponseFactory = Callable[[httpx.Request], httpx.Response]


class RecordingSleep:
    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, delay_seconds: float) -> None:
        self.delays.append(delay_seconds)


class ScriptedJira:
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.responses: list[httpx.Response | ResponseFactory | Exception] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        next_response = self.responses.pop(0)
        if isinstance(next_response, Exception):
            raise next_response
        if isinstance(next_response, httpx.Response):
            return next_response
        return next_response(request)


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


def json_response(payload: JsonValue, status_code: int = 200, headers: dict[str, str] | None = None) -> httpx.Response:
    return httpx.Response(status_code, json=payload, headers=headers)


def read_json_body(request: httpx.Request) -> JsonValue:
    body: JsonValue = json.loads(request.content)
    return body


def build_issue(issue_id: str, key: str, is_subtask: bool = False) -> JsonValue:
    return {
        "id": issue_id,
        "key": key,
        "fields": {
            "summary": f"Summary {key}",
            "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]},
            "status": {"name": "In Progress", "id": "3"},
            "issuetype": {"name": "Sub-task" if is_subtask else "Story", "subtask": is_subtask},
            "updated": "2026-10-30T09:15:00.000+0000",
        },
    }


async def test_get_myself_sends_basic_auth_and_maps_the_account(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [
        json_response({"accountId": "acc-9", "displayName": "Jira Bot", "emailAddress": None, "active": True})
    ]

    account = await jira_client.get_myself(CREDENTIALS)

    request = scripted_jira.requests[0]
    expected_authorization = base64.b64encode(b"bot@tessio.test:secret-jira-token").decode()
    assert request.method == "GET"
    assert str(request.url) == f"{SITE_URL}/rest/api/3/myself"
    assert request.headers["Authorization"] == f"Basic {expected_authorization}"
    assert request.headers["Accept"] == "application/json"
    assert account.account_id == "acc-9"
    assert account.display_name == "Jira Bot"
    assert account.email_address is None


async def test_unauthorized_or_forbidden_means_invalid_credentials(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [httpx.Response(401), httpx.Response(403)]

    with pytest.raises(JiraInvalidCredentialsError):
        await jira_client.get_myself(CREDENTIALS)
    with pytest.raises(JiraInvalidCredentialsError):
        await jira_client.list_projects(CREDENTIALS)


async def test_project_search_pages_until_is_last(jira_client: HttpxJiraClient, scripted_jira: ScriptedJira) -> None:
    scripted_jira.responses = [
        json_response(
            {
                "startAt": 0,
                "maxResults": 50,
                "isLast": False,
                "values": [{"id": "1", "key": "APP", "name": "Apple"}, {"id": "2", "key": "BAN", "name": "Banana"}],
            }
        ),
        json_response({"startAt": 2, "isLast": True, "values": [{"id": "3", "key": "CHE", "name": "Cherry"}]}),
    ]

    jira_projects = await jira_client.list_projects(CREDENTIALS)

    assert [jira_project.key for jira_project in jira_projects] == ["APP", "BAN", "CHE"]
    assert len(scripted_jira.requests) == 2
    first_parameters = scripted_jira.requests[0].url.params
    second_parameters = scripted_jira.requests[1].url.params
    assert scripted_jira.requests[0].url.path == "/rest/api/3/project/search"
    assert first_parameters["startAt"] == "0"
    assert first_parameters["maxResults"] == "50"
    assert first_parameters["orderBy"] == "name"
    assert second_parameters["startAt"] == "2"


async def test_boards_are_filtered_by_project_key(jira_client: HttpxJiraClient, scripted_jira: ScriptedJira) -> None:
    scripted_jira.responses = [
        json_response({"isLast": False, "values": [{"id": 9, "name": "Shop board", "type": "scrum"}]}),
        json_response({"isLast": True, "values": [{"id": 10, "name": "Shop flow", "type": "kanban"}]}),
    ]

    jira_boards = await jira_client.list_boards(CREDENTIALS, "SHOP")

    assert [(jira_board.id, jira_board.type) for jira_board in jira_boards] == [(9, "scrum"), (10, "kanban")]
    request = scripted_jira.requests[0]
    assert request.url.path == "/rest/agile/1.0/board"
    assert request.url.params["projectKeyOrId"] == "SHOP"
    assert request.url.params["maxResults"] == "50"
    assert scripted_jira.requests[1].url.params["startAt"] == "1"


async def test_boards_of_an_unknown_project_are_not_found(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [httpx.Response(400), httpx.Response(404)]

    with pytest.raises(JiraProjectNotFoundError):
        await jira_client.list_boards(CREDENTIALS, "NOPE")
    with pytest.raises(JiraProjectNotFoundError):
        await jira_client.list_boards(CREDENTIALS, "NOPE")


async def test_sprints_are_filtered_by_state_and_parse_dates(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [
        json_response(
            {
                "isLast": True,
                "values": [
                    {
                        "id": 41,
                        "name": "Sprint 41",
                        "state": "active",
                        "startDate": "2026-10-20T08:00:00.000Z",
                        "endDate": "2026-11-03T08:00:00.000Z",
                    },
                    {"id": 42, "name": "Sprint 42", "state": "future"},
                ],
            }
        )
    ]

    jira_sprints = await jira_client.list_sprints(
        CREDENTIALS, 7, frozenset({JiraSprintState.FUTURE, JiraSprintState.ACTIVE})
    )

    request = scripted_jira.requests[0]
    assert request.url.path == "/rest/agile/1.0/board/7/sprint"
    assert request.url.params["state"] == "active,future"
    assert jira_sprints[0].state is JiraSprintState.ACTIVE
    assert jira_sprints[0].start_at == datetime(2026, 10, 20, 8, tzinfo=UTC)
    assert jira_sprints[0].end_at == datetime(2026, 11, 3, 8, tzinfo=UTC)
    assert jira_sprints[0].complete_at is None
    assert jira_sprints[1].state is JiraSprintState.FUTURE
    assert jira_sprints[1].start_at is None


async def test_sprints_of_a_board_without_sprints_are_empty(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [json_response({"errorMessages": ["The board does not support sprints"]}, 400)]

    jira_sprints = await jira_client.list_sprints(CREDENTIALS, 3, frozenset({JiraSprintState.ACTIVE}))

    assert jira_sprints == []


async def test_issue_search_follows_the_next_page_token(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [
        json_response({"issues": [build_issue("100", "SHOP-1")], "nextPageToken": "page-2", "isLast": False}),
        json_response({"issues": [build_issue("101", "SHOP-2", is_subtask=True)], "isLast": True}),
    ]

    jira_issues = await jira_client.search_issues(CREDENTIALS, "sprint = 41")

    assert len(scripted_jira.requests) == 2
    first_request = scripted_jira.requests[0]
    assert first_request.method == "POST"
    assert first_request.url.path == "/rest/api/3/search/jql"
    assert read_json_body(first_request) == {
        "jql": "sprint = 41",
        "fields": ["summary", "description", "status", "issuetype", "updated"],
        "maxResults": 100,
    }
    second_body = read_json_body(scripted_jira.requests[1])
    assert isinstance(second_body, dict)
    assert second_body["nextPageToken"] == "page-2"
    assert [jira_issue.key for jira_issue in jira_issues] == ["SHOP-1", "SHOP-2"]
    first_issue = jira_issues[0]
    assert first_issue.summary == "Summary SHOP-1"
    assert first_issue.description == {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]}
    assert first_issue.status_name == "In Progress"
    assert first_issue.issue_type_name == "Story"
    assert first_issue.is_subtask is False
    assert first_issue.updated_at == datetime(2026, 10, 30, 9, 15, tzinfo=UTC)
    assert jira_issues[1].is_subtask is True


async def test_issue_search_stops_without_a_next_page_token(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    issue_without_description = build_issue("200", "SHOP-9")
    assert isinstance(issue_without_description, dict)
    fields = issue_without_description["fields"]
    assert isinstance(fields, dict)
    del fields["description"]
    scripted_jira.responses = [json_response({"issues": [issue_without_description]})]

    jira_issues = await jira_client.search_issues(CREDENTIALS, 'key = "SHOP-9"')

    assert len(scripted_jira.requests) == 1
    assert jira_issues[0].description is None


async def test_rate_limited_requests_wait_for_retry_after(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira, recording_sleep: RecordingSleep
) -> None:
    scripted_jira.responses = [
        httpx.Response(429, headers={"Retry-After": "2"}),
        json_response({"accountId": "acc-9", "displayName": "Jira Bot"}),
    ]

    account = await jira_client.get_myself(CREDENTIALS)

    assert account.account_id == "acc-9"
    assert recording_sleep.delays == [2.0]


async def test_retry_after_may_be_an_http_date(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira, recording_sleep: RecordingSleep
) -> None:
    retry_at = format_datetime(datetime.now(UTC) + timedelta(seconds=30), usegmt=True)
    scripted_jira.responses = [
        httpx.Response(503, headers={"Retry-After": retry_at}),
        json_response({"accountId": "acc-9", "displayName": "Jira Bot"}),
    ]

    await jira_client.get_myself(CREDENTIALS)

    assert len(recording_sleep.delays) == 1
    assert 25.0 <= recording_sleep.delays[0] <= 30.0


async def test_rate_limiting_gives_up_after_three_retries(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira, recording_sleep: RecordingSleep
) -> None:
    scripted_jira.responses = [httpx.Response(429) for _ in range(4)]

    with pytest.raises(JiraUnreachableError):
        await jira_client.get_myself(CREDENTIALS)

    assert len(scripted_jira.requests) == 4
    assert recording_sleep.delays == [1.0, 2.0, 4.0]


async def test_retry_after_is_capped(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira, recording_sleep: RecordingSleep
) -> None:
    scripted_jira.responses = [
        httpx.Response(429, headers={"Retry-After": "600"}),
        json_response({"accountId": "acc-9", "displayName": "Jira Bot"}),
    ]

    await jira_client.get_myself(CREDENTIALS)

    assert recording_sleep.delays == [60.0]


async def test_transport_failures_server_errors_and_bad_bodies_mean_unreachable(
    jira_client: HttpxJiraClient, scripted_jira: ScriptedJira
) -> None:
    scripted_jira.responses = [
        httpx.ConnectTimeout("timed out"),
        httpx.Response(500),
        httpx.Response(200, content=b"<html>not json</html>"),
        json_response({"accountId": "acc-9"}),
    ]

    for _ in range(4):
        with pytest.raises(JiraUnreachableError):
            await jira_client.get_myself(CREDENTIALS)


async def test_requests_use_the_jira_timeout(jira_client: HttpxJiraClient, scripted_jira: ScriptedJira) -> None:
    scripted_jira.responses = [json_response({"accountId": "acc-9", "displayName": "Jira Bot"})]

    await jira_client.get_myself(CREDENTIALS)

    timeout = scripted_jira.requests[0].extensions["timeout"]
    assert timeout == {"connect": 5.0, "read": 20.0, "write": 20.0, "pool": 20.0}
