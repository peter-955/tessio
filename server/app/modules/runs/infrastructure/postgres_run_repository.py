from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError

from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.errors import RunAlreadyRunningError, SuiteAlreadyRunningError
from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.typing.constants.run import RUNNING_RUN_PER_STORY_INDEX, RUNNING_RUN_PER_SUITE_INDEX
from app.modules.runs.typing.enums import RunStatus
from app.shared.postgres import Database, read_constraint_name


class PostgresRunRepository(RunRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, run_id: UUID) -> Run | None:
        row = await self._database.get_current_session().scalar(
            select(RunTable)
            .where(RunTable.project_id == project_id, RunTable.id == run_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else Run.model_validate(row)

    async def find_by_id_for_update(self, project_id: UUID, run_id: UUID) -> Run | None:
        row = await self._database.get_current_session().scalar(
            select(RunTable)
            .where(RunTable.project_id == project_id, RunTable.id == run_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Run.model_validate(row)

    async def has_running_for_story(self, project_id: UUID, story_id: UUID) -> bool:
        is_running = await self._database.get_current_session().scalar(
            select(
                exists().where(
                    RunTable.project_id == project_id,
                    RunTable.story_id == story_id,
                    RunTable.status == RunStatus.RUNNING,
                )
            )
        )
        return bool(is_running)

    async def has_running_for_suite(self, project_id: UUID, suite_id: UUID) -> bool:
        is_running = await self._database.get_current_session().scalar(
            select(
                exists().where(
                    RunTable.project_id == project_id,
                    RunTable.test_suite_id == suite_id,
                    RunTable.status == RunStatus.RUNNING,
                )
            )
        )
        return bool(is_running)

    async def is_environment_used(self, environment_id: UUID) -> bool:
        is_used = await self._database.get_current_session().scalar(
            select(exists().where(RunTable.environment_id == environment_id))
        )
        return bool(is_used)

    async def list_stale_run_ids(self, cutoff: datetime, limit: int) -> list[UUID]:
        run_ids = await self._database.get_current_session().scalars(
            select(RunTable.id)
            .where(RunTable.status == RunStatus.RUNNING, RunTable.last_activity_at < cutoff)
            .order_by(RunTable.last_activity_at, RunTable.id)
            .limit(limit)
        )
        return list(run_ids)

    async def find_stale_for_update(self, run_id: UUID, cutoff: datetime) -> Run | None:
        row = await self._database.get_current_session().scalar(
            select(RunTable)
            .where(
                RunTable.id == run_id,
                RunTable.status == RunStatus.RUNNING,
                RunTable.last_activity_at < cutoff,
            )
            .with_for_update(skip_locked=True)
            .execution_options(populate_existing=True)
        )
        return None if row is None else Run.model_validate(row)

    async def add(self, run: Run) -> None:
        session = self._database.get_current_session()
        session.add(RunTable(**self._build_values(run)))
        try:
            await session.flush()
        except IntegrityError as error:
            constraint_name = read_constraint_name(error)
            if constraint_name == RUNNING_RUN_PER_STORY_INDEX:
                raise RunAlreadyRunningError from error
            if constraint_name == RUNNING_RUN_PER_SUITE_INDEX:
                raise SuiteAlreadyRunningError from error
            raise

    async def save(self, run: Run) -> None:
        await self._database.get_current_session().merge(RunTable(**self._build_values(run)))

    @staticmethod
    def _build_values(run: Run) -> dict[str, object]:
        values = run.model_dump(exclude={"report", "skipped_cases"})
        values["report"] = None if run.report is None else run.report.model_dump(mode="json")
        values["skipped_cases"] = (
            None
            if run.skipped_cases is None
            else [skipped_case.model_dump(mode="json") for skipped_case in run.skipped_cases]
        )
        return values
