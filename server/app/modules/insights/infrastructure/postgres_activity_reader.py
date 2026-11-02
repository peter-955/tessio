from collections.abc import Collection
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select, union
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.failures.infrastructure import FailureTable
from app.modules.failures.typing.enums import FailureStatus
from app.modules.gaps.infrastructure import GapTable
from app.modules.gaps.typing.enums import GapSeverity, GapStatus
from app.modules.insights.domains.draft_case_item.entity import DraftCaseItem
from app.modules.insights.domains.draft_case_list.entity import DraftCaseList
from app.modules.insights.domains.failure_to_fix_item.entity import FailureToFixItem
from app.modules.insights.domains.failure_to_fix_list.entity import FailureToFixList
from app.modules.insights.domains.gap_to_answer_item.entity import GapToAnswerItem
from app.modules.insights.domains.gap_to_answer_list.entity import GapToAnswerList
from app.modules.insights.domains.run_reference.entity import RunReference
from app.modules.insights.ports.activity_reader import ActivityReader
from app.modules.insights.typing.constants import (
    ACTIVE_FAILURE_STATUSES,
    DRAFT_CASE_STATUSES,
    FAILURE_TO_FIX_STATUSES,
)
from app.modules.insights.utils.case_code import format_case_code
from app.modules.runs.infrastructure import RunCaseTable, RunTable
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.shared.permissions import ProjectRole
from app.shared.postgres import Database


class PostgresActivityReader(ActivityReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def count_open_gaps(self, project_id: UUID, story_ids: Collection[UUID]) -> dict[UUID, int]:
        if not story_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(GapTable.story_id, func.count(GapTable.id))
            .where(
                GapTable.project_id == project_id,
                GapTable.story_id.in_(story_ids),
                GapTable.status == GapStatus.OPEN,
            )
            .group_by(GapTable.story_id)
        )
        return dict(result.all())

    async def count_active_failures(self, project_id: UUID, story_ids: Collection[UUID]) -> dict[UUID, int]:
        if not story_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(TestCaseTable.story_id, func.count(FailureTable.id))
            .join(TestCaseTable, TestCaseTable.id == FailureTable.test_case_id)
            .where(
                FailureTable.project_id == project_id,
                TestCaseTable.story_id.in_(story_ids),
                FailureTable.status.in_(ACTIVE_FAILURE_STATUSES),
            )
            .group_by(TestCaseTable.story_id)
        )
        return dict(result.all())

    async def find_last_runs(self, project_id: UUID, story_ids: Collection[UUID]) -> dict[UUID, RunReference]:
        if not story_ids:
            return {}
        story_runs = select(
            RunTable.story_id.label("story_id"),
            RunTable.id.label("run_id"),
            RunTable.status.label("status"),
            RunTable.started_at.label("started_at"),
            RunTable.finished_at.label("finished_at"),
        ).where(RunTable.project_id == project_id, RunTable.story_id.in_(story_ids))
        storyless_runs = (
            select(
                TestCaseTable.story_id.label("story_id"),
                RunTable.id.label("run_id"),
                RunTable.status.label("status"),
                RunTable.started_at.label("started_at"),
                RunTable.finished_at.label("finished_at"),
            )
            .join(RunCaseTable, RunCaseTable.run_id == RunTable.id)
            .join(TestCaseTable, TestCaseTable.id == RunCaseTable.test_case_id)
            .where(
                RunTable.project_id == project_id,
                RunTable.story_id.is_(None),
                TestCaseTable.story_id.in_(story_ids),
            )
        )
        runs = union(story_runs, storyless_runs).subquery("story_runs")
        result = await self._database.get_current_session().execute(
            select(runs.c.story_id, runs.c.run_id, runs.c.status, runs.c.started_at, runs.c.finished_at)
            .ext(distinct_on(runs.c.story_id))
            .order_by(runs.c.story_id, runs.c.started_at.desc(), runs.c.run_id.desc())
        )
        return {
            story_id: RunReference(id=run_id, status=status, started_at=started_at, finished_at=finished_at)
            for story_id, run_id, status, started_at, finished_at in result
        }

    async def count_unassigned_failures(self, project_id: UUID) -> int:
        count: int | None = await self._database.get_current_session().scalar(
            select(func.count(FailureTable.id)).where(
                FailureTable.project_id == project_id,
                FailureTable.assignee_id.is_(None),
                FailureTable.status.in_(FAILURE_TO_FIX_STATUSES),
            )
        )
        return count or 0

    async def list_failures_to_fix(self, project_id: UUID, user_id: UUID, limit: int) -> FailureToFixList:
        conditions = (
            FailureTable.project_id == project_id,
            FailureTable.assignee_id == user_id,
            FailureTable.status.in_(FAILURE_TO_FIX_STATUSES),
        )
        session = self._database.get_current_session()
        total_count: int | None = await session.scalar(select(func.count(FailureTable.id)).where(*conditions))
        result = await session.execute(
            select(
                FailureTable.id,
                FailureTable.status,
                TestCaseTable.number,
                TestCaseTable.title,
                StoryTable.jira_key,
                FailureTable.created_at,
            )
            .join(TestCaseTable, TestCaseTable.id == FailureTable.test_case_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(*conditions)
            .order_by(FailureTable.created_at, FailureTable.id)
            .limit(limit)
        )
        items = [
            FailureToFixItem(
                failure_id=failure_id,
                status=FailureStatus(status),
                case_code=format_case_code(number),
                case_title=title,
                story_jira_key=jira_key,
                opened_at=created_at,
            )
            for failure_id, status, number, title, jira_key, created_at in result
        ]
        return FailureToFixList(total_count=total_count or 0, items=items)

    async def list_gaps_to_answer(
        self, project_id: UUID, user_id: UUID, role: ProjectRole, limit: int
    ) -> GapToAnswerList:
        conditions = (
            GapTable.project_id == project_id,
            GapTable.status == GapStatus.OPEN,
            or_(
                GapTable.assignee_id == user_id,
                and_(GapTable.assignee_id.is_(None), GapTable.assignee_role == role),
            ),
        )
        severity_rank = case(
            (GapTable.severity == GapSeverity.HIGH, 0), (GapTable.severity == GapSeverity.MEDIUM, 1), else_=2
        )
        session = self._database.get_current_session()
        total_count: int | None = await session.scalar(select(func.count(GapTable.id)).where(*conditions))
        result = await session.execute(
            select(GapTable, StoryTable.jira_key)
            .join(StoryTable, StoryTable.id == GapTable.story_id)
            .where(*conditions)
            .order_by(severity_rank, GapTable.created_at, GapTable.id)
            .limit(limit)
        )
        items = [
            GapToAnswerItem(
                gap_id=gap.id,
                story_jira_key=jira_key,
                question=gap.question,
                type=gap.type,
                severity=gap.severity,
                created_at=gap.created_at,
            )
            for gap, jira_key in result
        ]
        return GapToAnswerList(total_count=total_count or 0, items=items)

    async def list_draft_cases(self, project_id: UUID, user_id: UUID, limit: int) -> DraftCaseList:
        conditions = (
            TestCaseTable.project_id == project_id,
            TestCaseTable.created_by == user_id,
            TestCaseTable.status.in_(DRAFT_CASE_STATUSES),
        )
        session = self._database.get_current_session()
        total_count: int | None = await session.scalar(select(func.count(TestCaseTable.id)).where(*conditions))
        result = await session.execute(
            select(TestCaseTable, StoryTable.jira_key)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(*conditions)
            .order_by(TestCaseTable.created_at.desc(), TestCaseTable.id.desc())
            .limit(limit)
        )
        items = [
            DraftCaseItem(
                case_id=test_case.id,
                code=format_case_code(test_case.number),
                title=test_case.title,
                status=test_case.status,
                story_jira_key=jira_key,
            )
            for test_case, jira_key in result
        ]
        return DraftCaseList(total_count=total_count or 0, items=items)
