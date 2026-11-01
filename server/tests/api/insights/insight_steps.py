from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import count
from uuid import UUID, uuid4, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import DateTime, Text, Uuid, column, insert, table, update

from app.container import Container
from app.modules.failures.typing.enums import FailureStatus
from app.modules.gaps.infrastructure import GapTable
from app.modules.gaps.typing.enums import GapSeverity, GapStatus, GapTargetType, GapType
from app.modules.runs import ResultStatus, RunExecutor, RunStatus
from app.modules.runs.infrastructure import CaseResultTable, RunCaseTable, RunTable
from app.modules.stories import SprintState, TestStatus
from app.modules.stories.infrastructure import AcceptanceCriterionTable, SprintTable, StoryTable
from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.modules.test_cases.infrastructure import TestCaseCriterionTable, TestCaseTable, TestCaseVersionTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.shared.permissions import ProjectRole
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer

BASE_TIME = datetime(2026, 10, 1, 9, 0, tzinfo=UTC)
STORY_NUMBERS = count(1)
FAILURE_ROWS = table(
    "failures",
    column("id", Uuid()),
    column("project_id", Uuid()),
    column("story_id", Uuid()),
    column("test_case_id", Uuid()),
    column("opened_by_case_result_id", Uuid()),
    column("latest_case_result_id", Uuid()),
    column("assignee_id", Uuid()),
    column("status", Text()),
    column("created_at", DateTime(timezone=True)),
)


@dataclass(frozen=True)
class SeededStory:
    id: UUID
    jira_key: str
    title: str
    criterion_ids: dict[str, UUID]


@dataclass(frozen=True)
class SeededCase:
    id: UUID
    number: int
    story_id: UUID
    version_id: UUID

    @property
    def code(self) -> str:
        return f"TC-{self.number}"


@dataclass
class InsightWorld:
    project: SeededProject
    user_id: UUID
    environment_id: UUID
    case_count: int = 0
    sprint_count: int = 0

    def next_case_number(self) -> int:
        self.case_count += 1
        return self.case_count

    def next_jira_sprint_id(self) -> int:
        self.sprint_count += 1
        return self.sprint_count


async def sign_in_world(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.ADMIN,
) -> InsightWorld:
    project = await seed_project(container)
    user_id = await sign_up_member(client, container, recording_mailer, project, role)
    environment_id = await seed_environment(container, project)
    return InsightWorld(project=project, user_id=user_id, environment_id=environment_id)


async def seed_environment(container: Container, project: SeededProject) -> UUID:
    environment_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(EnvironmentTable).values(
                id=environment_id,
                project_id=project.id,
                name=f"Staging {environment_id.hex[:6]}",
                base_url="https://staging.shop.test",
                health_check_url=None,
                archived_at=None,
                created_at=datetime.now(UTC),
            )
        )
    return environment_id


async def seed_sprint(
    container: Container,
    world: InsightWorld,
    state: SprintState,
    start_at: datetime | None,
    jira_sprint_id: int | None = None,
) -> UUID:
    sprint_id = uuid7()
    sprint_number = jira_sprint_id if jira_sprint_id is not None else world.next_jira_sprint_id()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(SprintTable).values(
                id=sprint_id,
                project_id=world.project.id,
                jira_sprint_id=sprint_number,
                name=f"Sprint {sprint_number}",
                state=state,
                start_at=start_at,
                end_at=None if start_at is None else start_at + timedelta(days=14),
                complete_at=None,
                synced_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
            )
        )
    return sprint_id


async def seed_story(
    container: Container,
    world: InsightWorld,
    sprint_id: UUID | None = None,
    criterion_codes: tuple[str, ...] = (),
    is_missing: bool = False,
    test_status: TestStatus = TestStatus.NOT_STARTED,
    jira_key: str | None = None,
) -> SeededStory:
    story_id = uuid7()
    story_jira_key = jira_key or f"{world.project.key}-{next(STORY_NUMBERS)}"
    title = f"Story {story_jira_key}"
    now = datetime.now(UTC)
    criterion_ids = {code: uuid7() for code in criterion_codes}
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(StoryTable).values(
                id=story_id,
                project_id=world.project.id,
                sprint_id=sprint_id,
                jira_id=str(uuid4()),
                jira_key=story_jira_key,
                jira_url=f"https://team.atlassian.net/browse/{story_jira_key}",
                title=title,
                description=None,
                jira_status="In Progress",
                jira_issue_type="Story",
                test_status=test_status,
                jira_updated_at=now,
                synced_at=now,
                jira_missing_at=now if is_missing else None,
                created_at=now,
            )
        )
        for position, (code, criterion_id) in enumerate(criterion_ids.items(), start=1):
            await session.execute(
                insert(AcceptanceCriterionTable).values(
                    id=criterion_id,
                    story_id=story_id,
                    position=position,
                    code=code,
                    text=f"Criterion {code}",
                    removed_at=None,
                    created_at=now,
                )
            )
    return SeededStory(id=story_id, jira_key=story_jira_key, title=title, criterion_ids=criterion_ids)


async def remove_criterion(container: Container, criterion_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.id == criterion_id)
            .values(removed_at=datetime.now(UTC))
        )


async def seed_case(
    container: Container,
    world: InsightWorld,
    story: SeededStory,
    status: TestCaseStatus = TestCaseStatus.READY,
    criterion_codes: tuple[str, ...] = (),
    created_by: UUID | None = None,
    is_needing_review: bool = False,
    created_at: datetime | None = None,
) -> SeededCase:
    case_id = uuid7()
    version_id = uuid7()
    number = world.next_case_number()
    author_id = created_by or world.user_id
    now = created_at or datetime.now(UTC)
    criterion_ids = [story.criterion_ids[code] for code in criterion_codes]
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(TestCaseTable).values(
                id=case_id,
                project_id=world.project.id,
                story_id=story.id,
                number=number,
                title=f"Case {number}",
                priority=TestCasePriority.MEDIUM,
                status=status,
                current_version_id=None,
                needs_review_at=now if is_needing_review else None,
                needs_review_criterion_ids=[],
                created_by=author_id,
                created_at=now,
            )
        )
        await session.execute(
            insert(TestCaseVersionTable).values(
                id=version_id,
                test_case_id=case_id,
                number=1,
                title=f"Case {number}",
                priority=TestCasePriority.MEDIUM,
                business_value=None,
                preconditions=None,
                steps=[],
                criterion_ids=criterion_ids,
                data_keys=[],
                file_version_ids=[],
                created_by=author_id,
                created_at=now,
            )
        )
        for criterion_id in criterion_ids:
            await session.execute(
                insert(TestCaseCriterionTable).values(test_case_id=case_id, criterion_id=criterion_id, created_at=now)
            )
    return SeededCase(id=case_id, number=number, story_id=story.id, version_id=version_id)


async def seed_run(
    container: Container,
    world: InsightWorld,
    story: SeededStory,
    cases: tuple[SeededCase, ...] = (),
    status: RunStatus = RunStatus.PASSED,
    started_at: datetime = BASE_TIME,
) -> UUID:
    run_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(RunTable).values(
                id=run_id,
                project_id=world.project.id,
                story_id=story.id,
                environment_id=world.environment_id,
                executor=RunExecutor.CLAUDE,
                status=status,
                abort_reason=None,
                parent_run_id=None,
                started_by=world.user_id,
                started_via_token_id=None,
                summary=None,
                report=None,
                started_at=started_at,
                last_activity_at=started_at,
                finished_at=None if status is RunStatus.RUNNING else started_at + timedelta(minutes=5),
                created_at=started_at,
            )
        )
        for position, seeded_case in enumerate(cases, start=1):
            await session.execute(
                insert(RunCaseTable).values(
                    id=uuid7(),
                    run_id=run_id,
                    test_case_id=seeded_case.id,
                    test_case_version_id=seeded_case.version_id,
                    position=position,
                    created_at=started_at,
                )
            )
    return run_id


async def seed_result(
    container: Container,
    world: InsightWorld,
    run_id: UUID,
    seeded_case: SeededCase,
    status: ResultStatus,
    created_at: datetime = BASE_TIME,
    result_id: UUID | None = None,
) -> UUID:
    case_result_id = result_id or uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(CaseResultTable).values(
                id=case_result_id,
                run_id=run_id,
                test_case_id=seeded_case.id,
                test_case_version_id=seeded_case.version_id,
                status=status,
                duration_ms=1000,
                recorded_by=world.user_id,
                created_at=created_at,
            )
        )
    return case_result_id


async def seed_failure(
    container: Container,
    world: InsightWorld,
    seeded_case: SeededCase,
    status: FailureStatus = FailureStatus.OPEN,
    assignee_id: UUID | None = None,
    created_at: datetime = BASE_TIME,
) -> UUID:
    story = SeededStory(id=seeded_case.story_id, jira_key="", title="", criterion_ids={})
    run_id = await seed_run(container, world, story, (seeded_case,), RunStatus.FAILED, created_at)
    case_result_id = await seed_result(container, world, run_id, seeded_case, ResultStatus.FAILED, created_at)
    failure_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(FAILURE_ROWS).values(
                id=failure_id,
                project_id=world.project.id,
                story_id=seeded_case.story_id,
                test_case_id=seeded_case.id,
                opened_by_case_result_id=case_result_id,
                latest_case_result_id=case_result_id,
                assignee_id=assignee_id,
                status=status.value,
                created_at=created_at,
            )
        )
    return failure_id


async def seed_gap(
    container: Container,
    world: InsightWorld,
    story: SeededStory,
    assignee_id: UUID | None = None,
    assignee_role: ProjectRole | None = None,
    status: GapStatus = GapStatus.OPEN,
    severity: GapSeverity = GapSeverity.MEDIUM,
    created_at: datetime | None = None,
) -> UUID:
    gap_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(GapTable).values(
                id=gap_id,
                project_id=world.project.id,
                story_id=story.id,
                target_type=GapTargetType.STORY,
                target_id=None,
                type=GapType.MISSING_STEP,
                data_scope=None,
                severity=severity,
                question=f"Question {gap_id.hex[:6]}",
                status=status,
                assignee_id=assignee_id,
                assignee_role=assignee_role,
                raised_by=world.user_id,
                raised_via_token_id=None,
                answer=None if status is GapStatus.OPEN else "Answered.",
                answered_by=None if status is GapStatus.OPEN else world.user_id,
                answered_at=None if status is GapStatus.OPEN else datetime.now(UTC),
                reopened_by=None,
                reopened_at=None,
                created_at=created_at or datetime.now(UTC),
            )
        )
    return gap_id


async def get_ok(client: AsyncClient, url: str, params: dict[str, str] | None = None) -> Response:
    response = await client.get(url, params=params)
    assert response.status_code == 200, response.text
    return response
