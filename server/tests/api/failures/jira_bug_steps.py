from dataclasses import dataclass
from uuid import UUID

from httpx import AsyncClient, Response
from sqlalchemy import select, update

from app.container import Container
from app.modules.failures import CreateJiraIssueJobHandler
from app.modules.failures.infrastructure import FailureTable
from app.modules.jira.infrastructure import JiraConnectionTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable
from app.modules.stories import StorySource
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases.infrastructure import TestCaseVersionTable
from app.shared.permissions import ProjectRole
from tests.api.failures.failure_steps import (
    FailureScenario,
    SeededStep,
    find_only_failure,
    record,
    seed_scenario,
    seed_screenshot,
)
from tests.api.stories.story_steps import seed_jira_connection
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient

CASE_STEPS = [
    {"order": 1, "action": "Open the cart", "expected": "The cart lists one item"},
    {"order": 2, "action": "Pay by card", "expected": "The payment is accepted"},
    {"order": 3, "action": "Open the receipt", "expected": "The receipt shows the total"},
]
DATA_DRIVEN_STEPS = [
    {"order": 1, "action": "Open the cart", "expected": "The cart lists one item"},
    {"order": 2, "action": "Pay with card {{param.card}}", "expected": "The payment is {{ param.outcome }}"},
    {"order": 3, "action": "Open the receipt", "expected": "The receipt shows the total"},
]
DATA_ROWS = [
    {"card": "4242 4242 4242 4242", "outcome": "accepted"},
    {"card": "4000 0000 0000 0002", "outcome": "declined"},
]
ACTUAL_RESULT = "The card form shows 'Declined'"
STEP_ERROR = "AssertionError: payment status is declined"


@dataclass(frozen=True)
class JiraBugScenario:
    scenario: FailureScenario
    failure_id: UUID
    screenshot_file_id: UUID


def get_fake_jira_client(container: Container) -> FakeJiraClient:
    jira_client = container.jira_client
    assert isinstance(jira_client, FakeJiraClient)
    return jira_client


async def seed_jira_bug_scenario(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    runner_role: ProjectRole = ProjectRole.QC,
) -> JiraBugScenario:
    scenario = await seed_scenario(client, container, recording_mailer, runner_role)
    await seed_jira_connection(container, scenario.runner.user_id)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseVersionTable)
            .where(TestCaseVersionTable.id == scenario.case.version_id)
            .values(steps=CASE_STEPS, preconditions="A signed-in shopper with one item in the cart")
        )
    screenshot_file_id = await seed_screenshot(container, scenario.project, scenario.runner.user_id)
    await record(
        container,
        scenario,
        ResultStatus.FAILED,
        steps=(
            SeededStep(order=1, status=ResultStatus.PASSED, actual_result="The cart lists one item"),
            SeededStep(
                order=2,
                status=ResultStatus.FAILED,
                actual_result=ACTUAL_RESULT,
                error=STEP_ERROR,
                screenshot_file_id=screenshot_file_id,
            ),
        ),
    )
    failure = await find_only_failure(container, scenario.case.id)
    return JiraBugScenario(scenario=scenario, failure_id=failure.id, screenshot_file_id=screenshot_file_id)


async def make_failing_result_data_driven(container: Container, bug: JiraBugScenario, iteration: int) -> None:
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            update(TestCaseVersionTable)
            .where(TestCaseVersionTable.id == bug.scenario.case.version_id)
            .values(
                steps=DATA_DRIVEN_STEPS,
                preconditions="A shopper paying with {{param.card}}",
                parameters=["card", "outcome"],
                data_rows=DATA_ROWS,
            )
        )
        latest_case_result_id = await session.scalar(
            select(FailureTable.latest_case_result_id).where(FailureTable.id == bug.failure_id)
        )
        await session.execute(
            update(CaseResultTable).where(CaseResultTable.id == latest_case_result_id).values(iteration=iteration)
        )


async def request_jira_issue(client: AsyncClient, project_key: str, failure_id: UUID) -> Response:
    return await client.post(f"/api/projects/{project_key}/failures/{failure_id}/jira-issue")


async def preview_jira_issue(client: AsyncClient, project_key: str, failure_id: UUID) -> Response:
    return await client.get(f"/api/projects/{project_key}/failures/{failure_id}/jira-issue/preview")


async def run_create_issue_job(container: Container, bug: JiraBugScenario, requested_by: UUID | None = None) -> None:
    await CreateJiraIssueJobHandler(container.create_jira_issue).handle(
        {
            "projectId": str(bug.scenario.project.id),
            "failureId": str(bug.failure_id),
            "requestedBy": None if requested_by is None else str(requested_by),
        }
    )


async def find_failure_row(container: Container, failure_id: UUID) -> FailureTable:
    async with container.database.begin():
        row = await container.database.get_current_session().get(FailureTable, failure_id, populate_existing=True)
    assert row is not None
    return row


async def unlink_project_from_jira(container: Container, project_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project_id).values(jira_project_key=None, jira_board_id=None)
        )


async def set_bug_issue_type(container: Container, project_id: UUID, issue_type: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project_id).values(jira_bug_issue_type=issue_type)
        )


async def set_connection_create_access(container: Container, can_create_issues: bool | None) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(JiraConnectionTable).values(
                can_create_issues=can_create_issues,
                missing_permissions=[] if can_create_issues is not False else ["CREATE_ISSUES"],
            )
        )


async def mark_story_written_in_tessio(container: Container, story_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable).where(StoryTable.id == story_id).values(source=StorySource.TESSIO)
        )


async def set_failure_jira_issue(
    container: Container, failure_id: UUID, issue_key: str, status_name: str = "To Do"
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(FailureTable)
            .where(FailureTable.id == failure_id)
            .values(
                jira_issue_key=issue_key,
                jira_issue_url=f"https://team.atlassian.net/browse/{issue_key}",
                jira_issue_status=status_name,
            )
        )
