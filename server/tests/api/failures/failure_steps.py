from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable
from uuid import UUID, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import insert, select, update

from app.container import Container
from app.modules.failures import ApplyCaseResultUseCase, CountActiveFailuresUseCase
from app.modules.failures.infrastructure import FailureEventTable, FailureTable
from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.runs import RecordedCaseResult, ResultStatus, RunExecutor, RunStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable, StepResultTable
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases.infrastructure import TestCaseVersionTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import SeededStory, seed_story, seed_test_case, sign_up_account
from tests.api.projects.user_steps import SignedUpAccount
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer


@runtime_checkable
class FailuresContainer(Protocol):
    @property
    def apply_case_result(self) -> ApplyCaseResultUseCase: ...

    @property
    def count_active_failures(self) -> CountActiveFailuresUseCase: ...


@dataclass(frozen=True)
class SeededCase:
    id: UUID
    version_id: UUID
    number: int
    story_id: UUID


@dataclass(frozen=True)
class FailureScenario:
    project: SeededProject
    story: SeededStory
    case: SeededCase
    environment_id: UUID
    runner: SignedUpAccount


@dataclass(frozen=True)
class SeededStep:
    order: int
    status: ResultStatus
    actual_result: str | None = None
    error: str | None = None
    screenshot_file_id: UUID | None = None


@dataclass(frozen=True)
class RecordedResult:
    run_id: UUID
    case_result_id: UUID


def as_failures_container(container: Container) -> FailuresContainer:
    assert isinstance(container, FailuresContainer)
    return container


async def seed_environment(container: Container, project: SeededProject) -> UUID:
    environment_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(EnvironmentTable).values(
                id=environment_id,
                project_id=project.id,
                name=f"Staging {environment_id.hex[:6]}",
                base_url="https://staging.tessio.test",
                health_check_url=None,
                archived_at=None,
                created_at=datetime.now(UTC),
            )
        )
    return environment_id


async def seed_case(
    container: Container, project: SeededProject, story_id: UUID, number: int, created_by: UUID
) -> SeededCase:
    test_case_id = await seed_test_case(container, project, story_id, number, created_by)
    version_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(TestCaseVersionTable).values(
                id=version_id,
                test_case_id=test_case_id,
                number=1,
                title=f"Case {number}",
                priority="medium",
                business_value=None,
                preconditions=None,
                steps=[],
                criterion_ids=[],
                data_keys=[],
                file_version_ids=[],
                created_by=created_by,
                created_at=datetime.now(UTC),
            )
        )
    return SeededCase(id=test_case_id, version_id=version_id, number=number, story_id=story_id)


async def seed_scenario(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    runner_role: ProjectRole = ProjectRole.QC,
    case_number: int = 1,
) -> FailureScenario:
    project = await seed_project(container)
    story = await seed_story(container, project)
    runner = await sign_up_account(client, container, recording_mailer, project, runner_role, "Quinn Runner")
    case = await seed_case(container, project, story.id, case_number, runner.user_id)
    environment_id = await seed_environment(container, project)
    return FailureScenario(project=project, story=story, case=case, environment_id=environment_id, runner=runner)


async def seed_screenshot(container: Container, project: SeededProject, uploaded_by: UUID) -> UUID:
    file_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(StoredFileTable).values(
                id=file_id,
                project_id=project.id,
                kind=StoredFileKind.SCREENSHOT,
                object_key=f"projects/{project.id}/screenshot/{file_id}/step.png",
                file_name="step.png",
                content_type="image/png",
                size=10,
                sha256=None,
                status=StoredFileStatus.UPLOADED,
                uploaded_by=uploaded_by,
                created_at=datetime.now(UTC),
            )
        )
    return file_id


async def seed_run(
    container: Container,
    scenario: FailureScenario,
    status: RunStatus = RunStatus.FAILED,
    story_id: UUID | None = None,
) -> UUID:
    run_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(RunTable).values(
                id=run_id,
                project_id=scenario.project.id,
                story_id=story_id or scenario.story.id,
                environment_id=scenario.environment_id,
                executor=RunExecutor.CLAUDE,
                status=status,
                abort_reason=None,
                parent_run_id=None,
                started_by=scenario.runner.user_id,
                started_via_token_id=None,
                summary=None,
                report=None,
                started_at=now,
                last_activity_at=now,
                finished_at=now,
                created_at=now,
            )
        )
    return run_id


async def seed_case_result(
    container: Container,
    scenario: FailureScenario,
    run_id: UUID,
    case: SeededCase,
    status: ResultStatus,
    steps: tuple[SeededStep, ...] = (),
) -> RecordedCaseResult:
    case_result_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(CaseResultTable).values(
                id=case_result_id,
                run_id=run_id,
                test_case_id=case.id,
                test_case_version_id=case.version_id,
                status=status,
                duration_ms=1200,
                recorded_by=scenario.runner.user_id,
                created_at=now,
            )
        )
        for step in steps:
            await session.execute(
                insert(StepResultTable).values(
                    id=uuid7(),
                    case_result_id=case_result_id,
                    step_order=step.order,
                    status=step.status,
                    actual_result=step.actual_result,
                    error=step.error,
                    screenshot_file_id=step.screenshot_file_id,
                    evidence_file_id=None,
                    created_at=now,
                )
            )
    return RecordedCaseResult(
        project_id=scenario.project.id,
        story_id=case.story_id,
        run_id=run_id,
        case_result_id=case_result_id,
        test_case_id=case.id,
        status=status,
        suspected_cause=None,
        cause_reason=None,
        recorded_by=scenario.runner.user_id,
        recorded_at=now,
    )


async def record(
    container: Container,
    scenario: FailureScenario,
    status: ResultStatus,
    case: SeededCase | None = None,
    steps: tuple[SeededStep, ...] = (),
) -> RecordedResult:
    recorded_case = case or scenario.case
    run_id = await seed_run(container, scenario, story_id=recorded_case.story_id)
    recorded = await seed_case_result(container, scenario, run_id, recorded_case, status, steps)
    await as_failures_container(container).apply_case_result.handle(recorded)
    return RecordedResult(run_id=run_id, case_result_id=recorded.case_result_id)


async def list_failure_rows(container: Container, test_case_id: UUID) -> list[FailureTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(FailureTable)
            .where(FailureTable.test_case_id == test_case_id)
            .order_by(FailureTable.created_at, FailureTable.id)
        )
        return list(rows)


async def find_only_failure(container: Container, test_case_id: UUID) -> FailureTable:
    rows = await list_failure_rows(container, test_case_id)
    assert len(rows) == 1
    return rows[0]


async def list_event_rows(container: Container, failure_id: UUID) -> list[FailureEventTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(FailureEventTable)
            .where(FailureEventTable.failure_id == failure_id)
            .order_by(FailureEventTable.created_at, FailureEventTable.id)
        )
        return list(rows)


async def set_failure_status(container: Container, failure_id: UUID, status: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(FailureTable).where(FailureTable.id == failure_id).values(status=status)
        )


async def set_story_test_status(container: Container, story_id: UUID, test_status: StoryTestStatus) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable).where(StoryTable.id == story_id).values(test_status=test_status)
        )


async def open_failure(container: Container, scenario: FailureScenario) -> UUID:
    await record(container, scenario, ResultStatus.FAILED)
    row = await find_only_failure(container, scenario.case.id)
    return row.id


async def list_failure_notified_user_ids(container: Container, project: SeededProject, failure_id: UUID) -> list[UUID]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(NotificationTable).where(NotificationTable.project_id == project.id).order_by(NotificationTable.id)
        )
        return [row.user_id for row in rows if row.payload.get("failure_id") == str(failure_id)]


async def change_status(client: AsyncClient, project_key: str, failure_id: UUID, status: str) -> Response:
    return await client.put(f"/api/projects/{project_key}/failures/{failure_id}/status", json={"status": status})


async def assign(client: AsyncClient, project_key: str, failure_id: UUID, assignee_id: UUID | None) -> Response:
    return await client.put(
        f"/api/projects/{project_key}/failures/{failure_id}/assignee",
        json={"assigneeId": None if assignee_id is None else str(assignee_id)},
    )
