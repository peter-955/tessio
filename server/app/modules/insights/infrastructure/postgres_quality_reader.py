from datetime import datetime
from uuid import UUID

from sqlalchemy import Subquery, and_, exists, func, or_, select
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.insights.domains.case_share_counts.entity import CaseShareCounts
from app.modules.insights.domains.failing_case.entity import FailingCase
from app.modules.insights.domains.flaky_case.entity import FlakyCase
from app.modules.insights.domains.label_coverage.entity import LabelCoverage
from app.modules.insights.domains.label_coverage_report.entity import LabelCoverageReport
from app.modules.insights.ports.quality_reader import QualityReader
from app.modules.insights.typing.constants import FAILING_RESULT_STATUSES
from app.modules.insights.utils.case_code import format_case_code
from app.modules.labels.infrastructure import LabelTable, TestCaseLabelTable
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable, is_worst_iteration
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases import TestCaseStatus
from app.modules.test_cases.infrastructure import TestCaseTable
from app.shared.postgres import Database


class PostgresQualityReader(QualityReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def get_label_coverage(self, project_id: UUID) -> LabelCoverageReport:
        latest = self._select_latest_statuses(project_id)
        is_ready = TestCaseTable.status == TestCaseStatus.READY
        is_passed = latest.c.status == ResultStatus.PASSED
        counts = (
            func.count(TestCaseTable.id),
            func.count(TestCaseTable.id).filter(is_ready),
            func.count(TestCaseTable.id).filter(is_passed),
        )
        active_case = and_(TestCaseTable.project_id == project_id, TestCaseTable.status != TestCaseStatus.DEPRECATED)
        session = self._database.get_current_session()
        label_rows = await session.execute(
            select(LabelTable.id, LabelTable.name, LabelTable.color, *counts)
            .select_from(LabelTable)
            .outerjoin(TestCaseLabelTable, TestCaseLabelTable.label_id == LabelTable.id)
            .outerjoin(TestCaseTable, and_(TestCaseTable.id == TestCaseLabelTable.test_case_id, active_case))
            .outerjoin(latest, latest.c.test_case_id == TestCaseTable.id)
            .where(LabelTable.project_id == project_id)
            .group_by(LabelTable.id, LabelTable.name, LabelTable.color)
            .order_by(func.lower(LabelTable.name), LabelTable.id)
        )
        labels = [
            LabelCoverage(
                label_id=label_id,
                name=name,
                color=color,
                counts=CaseShareCounts(case_count=case_count, ready_count=ready_count, passed_count=passed_count),
            )
            for label_id, name, color, case_count, ready_count, passed_count in label_rows
        ]
        has_label = exists().where(TestCaseLabelTable.test_case_id == TestCaseTable.id).correlate(TestCaseTable)
        total_columns = [count.label(f"total_{index}") for index, count in enumerate(counts)]
        unlabelled_columns = [
            count.filter(~has_label).label(f"unlabelled_{index}") for index, count in enumerate(counts)
        ]
        totals = (
            await session.execute(
                select(*total_columns, *unlabelled_columns)
                .select_from(TestCaseTable)
                .outerjoin(latest, latest.c.test_case_id == TestCaseTable.id)
                .where(active_case)
            )
        ).one()
        total_values = [int(value) for value in totals]
        return LabelCoverageReport(
            labels=labels,
            unlabelled=CaseShareCounts(
                case_count=total_values[3], ready_count=total_values[4], passed_count=total_values[5]
            ),
            total=CaseShareCounts(
                case_count=total_values[0], ready_count=total_values[1], passed_count=total_values[2]
            ),
        )

    async def list_failing_cases(
        self, project_id: UUID, start_at: datetime, end_at: datetime, limit: int
    ) -> list[FailingCase]:
        is_failed = CaseResultTable.status == ResultStatus.FAILED
        is_blocked = CaseResultTable.status == ResultStatus.BLOCKED
        is_failing = CaseResultTable.status.in_(FAILING_RESULT_STATUSES)
        failing_count = func.count(CaseResultTable.id).filter(is_failing)
        last_failed_at = func.max(CaseResultTable.created_at).filter(is_failing)
        counts = (
            select(
                CaseResultTable.test_case_id.label("test_case_id"),
                func.count(CaseResultTable.id).label("result_count"),
                func.count(CaseResultTable.id).filter(is_failed).label("failed_count"),
                func.count(CaseResultTable.id).filter(is_blocked).label("blocked_count"),
                failing_count.label("failing_count"),
                last_failed_at.label("last_failed_at"),
            )
            .join(RunTable, RunTable.id == CaseResultTable.run_id)
            .where(
                RunTable.project_id == project_id,
                CaseResultTable.created_at >= start_at,
                CaseResultTable.created_at < end_at,
                CaseResultTable.status != ResultStatus.SKIPPED,
                is_worst_iteration(),
            )
            .group_by(CaseResultTable.test_case_id)
            .having(failing_count > 0)
            .subquery("failing_counts")
        )
        result = await self._database.get_current_session().execute(
            select(
                TestCaseTable,
                StoryTable.jira_key,
                counts.c.result_count,
                counts.c.failed_count,
                counts.c.blocked_count,
                counts.c.last_failed_at,
            )
            .join(counts, counts.c.test_case_id == TestCaseTable.id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .order_by(
                counts.c.failing_count.desc(),
                (counts.c.failing_count * 1.0 / counts.c.result_count).desc(),
                counts.c.last_failed_at.desc(),
                TestCaseTable.number,
            )
            .limit(limit)
        )
        return [
            FailingCase(
                test_case_id=row.id,
                code=format_case_code(row.number),
                title=row.title,
                status=row.status,
                story_jira_key=jira_key,
                result_count=result_count,
                failed_count=failed_count,
                blocked_count=blocked_count,
                last_failed_at=failed_at,
                is_flaky=row.flaky_since is not None,
                is_quarantined=row.quarantined_at is not None,
            )
            for row, jira_key, result_count, failed_count, blocked_count, failed_at in result
        ]

    async def list_flaky_cases(self, project_id: UUID, limit: int) -> list[FlakyCase]:
        result = await self._database.get_current_session().execute(
            select(TestCaseTable, StoryTable.jira_key)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(
                TestCaseTable.project_id == project_id,
                TestCaseTable.status != TestCaseStatus.DEPRECATED,
                or_(TestCaseTable.flaky_since.is_not(None), TestCaseTable.disagreed_at.is_not(None)),
            )
            .order_by(
                TestCaseTable.flaky_score.desc(),
                TestCaseTable.flaky_since.asc().nulls_last(),
                TestCaseTable.disagreed_at.desc().nulls_last(),
                TestCaseTable.number,
            )
            .limit(limit)
        )
        return [
            FlakyCase(
                test_case_id=row.id,
                code=format_case_code(row.number),
                title=row.title,
                status=row.status,
                story_jira_key=jira_key,
                flaky_score=row.flaky_score,
                flaky_since=row.flaky_since,
                disagreed_at=row.disagreed_at,
                quarantined_at=row.quarantined_at,
            )
            for row, jira_key in result
        ]

    @staticmethod
    def _select_latest_statuses(project_id: UUID) -> Subquery:
        return (
            select(CaseResultTable.test_case_id, CaseResultTable.status)
            .ext(distinct_on(CaseResultTable.test_case_id))
            .join(TestCaseTable, TestCaseTable.id == CaseResultTable.test_case_id)
            .where(TestCaseTable.project_id == project_id, is_worst_iteration())
            .order_by(
                CaseResultTable.test_case_id,
                (CaseResultTable.status == ResultStatus.SKIPPED).asc(),
                CaseResultTable.created_at.desc(),
                CaseResultTable.id.desc(),
            )
            .subquery("latest_statuses")
        )
