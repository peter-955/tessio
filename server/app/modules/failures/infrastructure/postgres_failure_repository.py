from datetime import datetime
from uuid import UUID

from sqlalchemy import Row, Select, func, select
from sqlalchemy.orm import aliased

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_filter.entity import FailureFilter
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.infrastructure.failure_table import FailureTable
from app.modules.failures.typing.constants import ACTIVE_FAILURE_STATUSES
from app.modules.failures.typing.enums import FailureStatus
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.infrastructure import CaseResultTable
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database

type FailureViewRow = Row[
    FailureTable, str, str, str, int, str, str | None, UserStatus | None, str | None, UUID, datetime
]


class PostgresFailureRepository(FailureRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_for_update(self, project_id: UUID, failure_id: UUID) -> Failure | None:
        row = await self._database.get_current_session().scalar(
            select(FailureTable)
            .where(FailureTable.project_id == project_id, FailureTable.id == failure_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Failure.model_validate(row)

    async def lock_test_case(self, test_case_id: UUID) -> None:
        await self._database.get_current_session().execute(
            select(func.pg_advisory_xact_lock(func.hashtextextended(str(test_case_id), 0)))
        )

    async def find_active_for_update(self, test_case_id: UUID) -> Failure | None:
        row = await self._database.get_current_session().scalar(
            select(FailureTable)
            .where(FailureTable.test_case_id == test_case_id, FailureTable.status != FailureStatus.VERIFIED)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Failure.model_validate(row)

    async def add(self, failure: Failure) -> None:
        session = self._database.get_current_session()
        session.add(FailureTable(**failure.model_dump()))
        await session.flush()

    async def save(self, failure: Failure) -> None:
        session = self._database.get_current_session()
        await session.merge(FailureTable(**failure.model_dump()))
        await session.flush()

    async def count_active_for_story(self, project_id: UUID, story_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(FailureTable)
            .where(
                FailureTable.project_id == project_id,
                FailureTable.story_id == story_id,
                FailureTable.status.in_(ACTIVE_FAILURE_STATUSES),
            )
        )
        return count or 0

    async def find_view(self, project_id: UUID, failure_id: UUID) -> FailureView | None:
        result = await self._database.get_current_session().execute(
            self._select_views().where(FailureTable.project_id == project_id, FailureTable.id == failure_id)
        )
        row = result.one_or_none()
        return None if row is None else self._build_view(row)

    async def list_views(self, project_id: UUID, failure_filter: FailureFilter, limit: int) -> list[FailureView]:
        statement = self._select_views().where(FailureTable.project_id == project_id)
        if failure_filter.statuses:
            statement = statement.where(FailureTable.status.in_(failure_filter.statuses))
        if failure_filter.assignee_id is not None:
            statement = statement.where(FailureTable.assignee_id == failure_filter.assignee_id)
        if failure_filter.is_unassigned:
            statement = statement.where(FailureTable.assignee_id.is_(None))
        if failure_filter.story_jira_key is not None:
            statement = statement.where(StoryTable.jira_key == failure_filter.story_jira_key)
        if failure_filter.test_case_id is not None:
            statement = statement.where(FailureTable.test_case_id == failure_filter.test_case_id)
        result = await self._database.get_current_session().execute(statement.limit(limit))
        return [self._build_view(row) for row in result]

    @staticmethod
    def _select_views() -> Select[
        FailureTable, str, str, str, int, str, str | None, UserStatus | None, str | None, UUID, datetime
    ]:
        assignee = aliased(UserTable)
        status_changer = aliased(UserTable)
        return (
            select(
                FailureTable,
                ProjectTable.key,
                StoryTable.jira_key,
                StoryTable.title,
                TestCaseTable.number,
                TestCaseTable.title,
                assignee.name,
                assignee.status,
                status_changer.name,
                CaseResultTable.run_id,
                CaseResultTable.created_at,
            )
            .join(ProjectTable, ProjectTable.id == FailureTable.project_id)
            .join(StoryTable, StoryTable.id == FailureTable.story_id)
            .join(TestCaseTable, TestCaseTable.id == FailureTable.test_case_id)
            .join(CaseResultTable, CaseResultTable.id == FailureTable.latest_case_result_id)
            .outerjoin(assignee, assignee.id == FailureTable.assignee_id)
            .outerjoin(status_changer, status_changer.id == FailureTable.status_changed_by)
            .order_by(FailureTable.created_at.desc(), FailureTable.id.desc())
        )

    @staticmethod
    def _build_view(row: FailureViewRow) -> FailureView:
        (
            failure_row,
            project_key,
            story_jira_key,
            story_title,
            test_case_number,
            test_case_title,
            assignee_name,
            assignee_status,
            status_changed_by_name,
            latest_run_id,
            latest_failed_at,
        ) = row
        return FailureView(
            failure=Failure.model_validate(failure_row),
            project_key=project_key,
            story_jira_key=story_jira_key,
            story_title=story_title,
            test_case_number=test_case_number,
            test_case_title=test_case_title,
            assignee_name=assignee_name,
            assignee_status=assignee_status,
            status_changed_by_name=status_changed_by_name,
            latest_run_id=latest_run_id,
            latest_failed_at=latest_failed_at,
        )
