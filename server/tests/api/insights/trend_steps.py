from datetime import datetime, timedelta
from uuid import UUID, uuid7

from sqlalchemy import insert, update

from app.container import Container
from app.modules.failures.infrastructure import FailureEventTable
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.gaps.infrastructure import GapTable
from app.modules.labels import LabelColor
from app.modules.labels.infrastructure import LabelTable, TestCaseLabelTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.run_logs.infrastructure import RunLogTable
from app.modules.runs import ResultStatus, RunStatus
from app.modules.runs.infrastructure import CaseResultTable, RunCaseTable, RunTable
from app.modules.suites.infrastructure import TestSuiteTable
from app.modules.test_cases.infrastructure import TestCaseTable
from tests.api.insights.insight_steps import BASE_TIME, InsightWorld, SeededCase, SeededStory


async def backdate_project(container: Container, world: InsightWorld, created_at: datetime) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == world.project.id).values(created_at=created_at)
        )


async def seed_suite(container: Container, world: InsightWorld, name: str) -> UUID:
    suite_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(TestSuiteTable).values(
                id=suite_id,
                project_id=world.project.id,
                name=name,
                description=None,
                archived_at=None,
                created_by=world.user_id,
                created_at=BASE_TIME,
            )
        )
    return suite_id


async def seed_any_run(
    container: Container,
    world: InsightWorld,
    cases: tuple[SeededCase, ...],
    started_at: datetime,
    executor: str = "claude",
    story: SeededStory | None = None,
    suite_id: UUID | None = None,
    status: RunStatus = RunStatus.PASSED,
) -> UUID:
    run_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(RunTable).values(
                id=run_id,
                project_id=world.project.id,
                story_id=None if story is None else story.id,
                test_suite_id=suite_id,
                environment_id=world.environment_id,
                executor=executor,
                status=status.value,
                abort_reason=None,
                parent_run_id=None,
                started_by=world.user_id,
                started_via_token_id=None,
                summary=None,
                report=None,
                started_at=started_at,
                last_activity_at=started_at,
                finished_at=started_at + timedelta(minutes=5),
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


async def seed_iteration_result(
    container: Container,
    world: InsightWorld,
    run_id: UUID,
    seeded_case: SeededCase,
    status: ResultStatus,
    created_at: datetime,
    iteration: int = 0,
) -> UUID:
    case_result_id = uuid7()
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
                iteration=iteration,
            )
        )
    return case_result_id


async def seed_failure_status_event(
    container: Container, failure_id: UUID, to_status: FailureStatus, created_at: datetime
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(FailureEventTable).values(
                id=uuid7(),
                failure_id=failure_id,
                kind=FailureEventKind.STATUS_CHANGED,
                from_status=FailureStatus.OPEN,
                to_status=to_status,
                from_cause=None,
                to_cause=None,
                case_result_id=None,
                assignee_id=None,
                actor_id=None,
                created_at=created_at,
            )
        )


async def answer_gap(container: Container, gap_id: UUID, answered_at: datetime) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(GapTable)
            .where(GapTable.id == gap_id)
            .values(status="resolved", answer="Answered.", answered_at=answered_at)
        )


async def seed_run_log(
    container: Container,
    run_id: UUID,
    input_tokens: int,
    output_tokens: int,
    cache_read_input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(RunLogTable).values(
                run_id=run_id,
                received_at=BASE_TIME,
                is_cut=False,
                input_tokens=input_tokens,
                cache_creation_input_tokens=cache_creation_input_tokens,
                cache_read_input_tokens=cache_read_input_tokens,
                output_tokens=output_tokens,
            )
        )


async def seed_label(container: Container, world: InsightWorld, name: str, cases: tuple[SeededCase, ...]) -> UUID:
    label_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(LabelTable).values(
                id=label_id,
                project_id=world.project.id,
                name=name,
                color=LabelColor.BLUE,
                created_by=world.user_id,
                created_at=BASE_TIME,
            )
        )
        for seeded_case in cases:
            await session.execute(
                insert(TestCaseLabelTable).values(test_case_id=seeded_case.id, label_id=label_id, created_at=BASE_TIME)
            )
    return label_id


async def mark_case_quality(
    container: Container,
    seeded_case: SeededCase,
    flaky_score: int = 0,
    flaky_since: datetime | None = None,
    disagreed_at: datetime | None = None,
    quarantined_at: datetime | None = None,
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseTable)
            .where(TestCaseTable.id == seeded_case.id)
            .values(
                flaky_score=flaky_score,
                flaky_since=flaky_since,
                disagreed_at=disagreed_at,
                quarantined_at=quarantined_at,
            )
        )
