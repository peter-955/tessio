from collections.abc import Collection
from uuid import UUID

from sqlalchemy import Subquery, func, select
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.insights.domains.latest_result.entity import LatestResult
from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.domains.traced_criterion.entity import TracedCriterion
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.utils.case_code import format_case_code
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable, RunCaseTable, RunTable, is_worst_iteration
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.test_cases import TestCaseStatus
from app.modules.test_cases.infrastructure import TestCaseCriterionTable, TestCaseTable
from app.shared.postgres import Database


class PostgresCoverageReader(CoverageReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_criteria(self, project_id: UUID, story_ids: Collection[UUID]) -> list[TracedCriterion]:
        if not story_ids:
            return []
        rows = await self._database.get_current_session().scalars(
            select(AcceptanceCriterionTable)
            .join(StoryTable, StoryTable.id == AcceptanceCriterionTable.story_id)
            .where(StoryTable.project_id == project_id, AcceptanceCriterionTable.story_id.in_(story_ids))
            .order_by(AcceptanceCriterionTable.story_id, AcceptanceCriterionTable.position)
        )
        return [
            TracedCriterion(
                id=row.id,
                story_id=row.story_id,
                code=row.code,
                position=row.position,
                text=row.text,
                removed_at=row.removed_at,
            )
            for row in rows
        ]

    async def list_cases(
        self, project_id: UUID, story_ids: Collection[UUID] | None, is_including_deprecated: bool
    ) -> list[TracedCase]:
        if story_ids is not None and not story_ids:
            return []
        latest = self._select_latest_results(project_id, story_ids)
        criterion_ids = (
            select(func.array_agg(TestCaseCriterionTable.criterion_id))
            .where(TestCaseCriterionTable.test_case_id == TestCaseTable.id)
            .correlate(TestCaseTable)
            .scalar_subquery()
        )
        statement = (
            select(
                TestCaseTable,
                criterion_ids,
                latest.c.id,
                latest.c.run_id,
                latest.c.status,
                latest.c.created_at,
                latest.c.test_case_version_id,
            )
            .outerjoin(latest, latest.c.test_case_id == TestCaseTable.id)
            .where(TestCaseTable.project_id == project_id)
            .order_by(TestCaseTable.number)
        )
        if story_ids is not None:
            statement = statement.where(TestCaseTable.story_id.in_(story_ids))
        if not is_including_deprecated:
            statement = statement.where(TestCaseTable.status != TestCaseStatus.DEPRECATED)
        result = await self._database.get_current_session().execute(statement)
        cases: list[TracedCase] = []
        for row, linked_ids, result_id, run_id, status, recorded_at, version_id in result:
            latest_result = (
                None
                if result_id is None
                else LatestResult(
                    case_result_id=result_id,
                    run_id=run_id,
                    status=status,
                    recorded_at=recorded_at,
                    test_case_version_id=version_id,
                )
            )
            cases.append(
                TracedCase(
                    id=row.id,
                    story_id=row.story_id,
                    number=row.number,
                    code=format_case_code(row.number),
                    title=row.title,
                    status=row.status,
                    priority=row.priority,
                    is_needing_review=row.needs_review_at is not None,
                    created_by=row.created_by,
                    criterion_ids=frozenset(linked_ids or ()),
                    latest_result=latest_result,
                    is_flaky=row.flaky_since is not None,
                    is_disagreeing=row.disagreed_at is not None,
                    is_quarantined=row.quarantined_at is not None,
                )
            )
        return cases

    async def find_run_story_id(self, project_id: UUID, run_id: UUID) -> UUID | None:
        story_id: UUID | None = await self._database.get_current_session().scalar(
            select(RunTable.story_id).where(RunTable.project_id == project_id, RunTable.id == run_id)
        )
        return story_id

    async def list_run_case_story_keys(self, project_id: UUID, run_id: UUID) -> dict[UUID, str]:
        result = await self._database.get_current_session().execute(
            select(StoryTable.id, StoryTable.jira_key, func.min(RunCaseTable.position).label("first_position"))
            .select_from(RunCaseTable)
            .join(RunTable, RunTable.id == RunCaseTable.run_id)
            .join(TestCaseTable, TestCaseTable.id == RunCaseTable.test_case_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(RunTable.project_id == project_id, RunCaseTable.run_id == run_id)
            .group_by(StoryTable.id, StoryTable.jira_key)
            .order_by("first_position")
        )
        return {story_id: jira_key for story_id, jira_key, _ in result}

    async def list_run_outcomes(self, project_id: UUID, run_id: UUID) -> dict[UUID, ResultStatus | None]:
        result = await self._database.get_current_session().execute(
            select(RunCaseTable.test_case_id, CaseResultTable.status)
            .join(RunTable, RunTable.id == RunCaseTable.run_id)
            .outerjoin(
                CaseResultTable,
                (CaseResultTable.run_id == RunCaseTable.run_id)
                & (CaseResultTable.test_case_id == RunCaseTable.test_case_id)
                & is_worst_iteration(),
            )
            .where(RunTable.project_id == project_id, RunCaseTable.run_id == run_id)
        )
        return dict(result.all())

    @staticmethod
    def _select_latest_results(project_id: UUID, story_ids: Collection[UUID] | None) -> Subquery:
        statement = (
            select(
                CaseResultTable.test_case_id,
                CaseResultTable.id,
                CaseResultTable.run_id,
                CaseResultTable.status,
                CaseResultTable.created_at,
                CaseResultTable.test_case_version_id,
            )
            .ext(distinct_on(CaseResultTable.test_case_id))
            .join(TestCaseTable, TestCaseTable.id == CaseResultTable.test_case_id)
            .where(TestCaseTable.project_id == project_id, is_worst_iteration())
            .order_by(
                CaseResultTable.test_case_id,
                (CaseResultTable.status == ResultStatus.SKIPPED).asc(),
                CaseResultTable.created_at.desc(),
                CaseResultTable.id.desc(),
            )
        )
        if story_ids is not None:
            statement = statement.where(TestCaseTable.story_id.in_(story_ids))
        return statement.subquery("latest_results")
