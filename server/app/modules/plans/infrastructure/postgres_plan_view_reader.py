from collections.abc import Collection
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.failures.infrastructure import FailureTable
from app.modules.failures.typing.constants import ACTIVE_FAILURE_STATUSES
from app.modules.gaps import GapStatus
from app.modules.gaps.infrastructure import GapTable
from app.modules.plans.domains.plan_case.entity import PlanCase
from app.modules.plans.domains.plan_failure_blocker.entity import PlanFailureBlocker
from app.modules.plans.domains.plan_gap_blocker.entity import PlanGapBlocker
from app.modules.plans.domains.plan_item_view.entity import PlanItemView
from app.modules.plans.domains.plan_latest_result.entity import PlanLatestResult
from app.modules.plans.domains.plan_progress_window.entity import PlanProgressWindow
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.modules.plans.infrastructure.test_plan_item_table import TestPlanItemTable
from app.modules.plans.infrastructure.test_plan_table import TestPlanTable
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.typing.enums import PlanItemKind, PlanStatus
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable, is_worst_iteration
from app.modules.stories.infrastructure import StoryTable
from app.modules.suites.infrastructure import TestSuiteCaseTable, TestSuiteTable
from app.modules.test_cases import TestCaseStatus
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.test_cases.typing.constants import CASE_CODE_PREFIX
from app.modules.test_data.infrastructure import EnvironmentTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database

PLAN_CASE_COLUMNS = (
    TestCaseTable.id,
    TestCaseTable.number,
    TestCaseTable.title,
    TestCaseTable.status,
    TestCaseTable.priority,
    TestCaseTable.needs_review_at,
    TestCaseTable.story_id,
    StoryTable.jira_key,
    StoryTable.title,
)


class PostgresPlanViewReader(PlanViewReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_plans(self, project_id: UUID, status: PlanStatus | None) -> list[TestPlan]:
        statement = (
            select(TestPlanTable)
            .where(TestPlanTable.project_id == project_id)
            .order_by(TestPlanTable.created_at.desc(), TestPlanTable.id.desc())
        )
        if status is not None:
            statement = statement.where(TestPlanTable.status == status)
        rows = await self._database.get_current_session().scalars(statement)
        return [TestPlan.model_validate(row) for row in rows]

    async def count_items(self, plan_ids: Collection[UUID]) -> dict[UUID, int]:
        if not plan_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(TestPlanItemTable.test_plan_id, func.count())
            .where(TestPlanItemTable.test_plan_id.in_(plan_ids))
            .group_by(TestPlanItemTable.test_plan_id)
        )
        return dict(result.all())

    async def list_item_views(self, plan_id: UUID) -> list[PlanItemView]:
        session = self._database.get_current_session()
        suite_case_count = (
            select(func.count())
            .select_from(TestSuiteCaseTable)
            .join(TestCaseTable, TestCaseTable.id == TestSuiteCaseTable.test_case_id)
            .where(
                TestSuiteCaseTable.test_suite_id == TestSuiteTable.id,
                TestCaseTable.status != TestCaseStatus.DEPRECATED,
            )
            .scalar_subquery()
        )
        story_case_count = (
            select(func.count())
            .select_from(TestCaseTable)
            .where(TestCaseTable.story_id == StoryTable.id, TestCaseTable.status != TestCaseStatus.DEPRECATED)
            .scalar_subquery()
        )
        suite_rows = await session.execute(
            select(
                TestPlanItemTable.position,
                TestSuiteTable.id,
                TestSuiteTable.name,
                TestSuiteTable.archived_at,
                suite_case_count,
            )
            .join(TestSuiteTable, TestSuiteTable.id == TestPlanItemTable.test_suite_id)
            .where(TestPlanItemTable.test_plan_id == plan_id)
        )
        story_rows = await session.execute(
            select(TestPlanItemTable.position, StoryTable.id, StoryTable.jira_key, StoryTable.title, story_case_count)
            .join(StoryTable, StoryTable.id == TestPlanItemTable.story_id)
            .where(TestPlanItemTable.test_plan_id == plan_id)
        )
        views = [
            PlanItemView(
                position=position,
                kind=PlanItemKind.SUITE,
                test_suite_id=suite_id,
                story_id=None,
                name=name,
                story_jira_key=None,
                archived_at=archived_at,
                case_count=case_count,
            )
            for position, suite_id, name, archived_at, case_count in suite_rows
        ] + [
            PlanItemView(
                position=position,
                kind=PlanItemKind.STORY,
                test_suite_id=None,
                story_id=story_id,
                name=title,
                story_jira_key=jira_key,
                archived_at=None,
                case_count=case_count,
            )
            for position, story_id, jira_key, title, case_count in story_rows
        ]
        return sorted(views, key=lambda view: view.position)

    async def list_plan_cases(self, plan_id: UUID) -> list[PlanCase]:
        session = self._database.get_current_session()
        suite_rows = await session.execute(
            select(TestPlanItemTable.position, TestSuiteCaseTable.position, *PLAN_CASE_COLUMNS)
            .join(TestSuiteCaseTable, TestSuiteCaseTable.test_suite_id == TestPlanItemTable.test_suite_id)
            .join(TestCaseTable, TestCaseTable.id == TestSuiteCaseTable.test_case_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(TestPlanItemTable.test_plan_id == plan_id, TestCaseTable.status != TestCaseStatus.DEPRECATED)
        )
        story_rows = await session.execute(
            select(TestPlanItemTable.position, TestCaseTable.number, *PLAN_CASE_COLUMNS)
            .join(TestCaseTable, TestCaseTable.story_id == TestPlanItemTable.story_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(TestPlanItemTable.test_plan_id == plan_id, TestCaseTable.status != TestCaseStatus.DEPRECATED)
        )
        ordered_rows = sorted([*suite_rows, *story_rows], key=lambda row: (row[0], row[1]))
        cases: dict[UUID, PlanCase] = {}
        for (
            _,
            _,
            case_id,
            number,
            title,
            status,
            priority,
            needs_review_at,
            story_id,
            jira_key,
            story_title,
        ) in ordered_rows:
            if case_id in cases:
                continue
            cases[case_id] = PlanCase(
                test_case_id=case_id,
                code=f"{CASE_CODE_PREFIX}{number}",
                title=title,
                status=status,
                priority=priority,
                is_needing_review=needs_review_at is not None,
                story_id=story_id,
                story_jira_key=jira_key,
                story_title=story_title,
            )
        return list(cases.values())

    async def list_plan_story_ids(self, plan_id: UUID) -> set[UUID]:
        story_ids = await self._database.get_current_session().scalars(
            select(TestPlanItemTable.story_id).where(
                TestPlanItemTable.test_plan_id == plan_id, TestPlanItemTable.story_id.is_not(None)
            )
        )
        return {story_id for story_id in story_ids if story_id is not None}

    async def map_latest_results(
        self, test_case_ids: Collection[UUID], window: PlanProgressWindow
    ) -> dict[UUID, PlanLatestResult]:
        if not test_case_ids:
            return {}
        statement = (
            select(
                CaseResultTable.test_case_id,
                CaseResultTable.id,
                CaseResultTable.run_id,
                CaseResultTable.status,
                CaseResultTable.created_at,
            )
            .ext(distinct_on(CaseResultTable.test_case_id))
            .join(RunTable, RunTable.id == CaseResultTable.run_id)
            .where(
                RunTable.project_id == window.project_id,
                CaseResultTable.test_case_id.in_(test_case_ids),
                CaseResultTable.created_at >= window.since,
                is_worst_iteration(),
            )
            .order_by(
                CaseResultTable.test_case_id,
                (CaseResultTable.status == ResultStatus.SKIPPED).asc(),
                CaseResultTable.created_at.desc(),
                CaseResultTable.id.desc(),
            )
        )
        if window.until is not None:
            statement = statement.where(CaseResultTable.created_at <= window.until)
        if window.environment_id is not None:
            statement = statement.where(RunTable.environment_id == window.environment_id)
        result = await self._database.get_current_session().execute(statement)
        return {
            test_case_id: PlanLatestResult(
                case_result_id=case_result_id, run_id=run_id, status=status, recorded_at=recorded_at
            )
            for test_case_id, case_result_id, run_id, status, recorded_at in result
        }

    async def list_failure_blockers(
        self, project_id: UUID, test_case_ids: Collection[UUID]
    ) -> list[PlanFailureBlocker]:
        if not test_case_ids:
            return []
        result = await self._database.get_current_session().execute(
            select(
                FailureTable.id,
                FailureTable.test_case_id,
                TestCaseTable.number,
                TestCaseTable.title,
                StoryTable.jira_key,
                FailureTable.status,
                FailureTable.assignee_id,
                UserTable.name,
                FailureTable.created_at,
            )
            .join(TestCaseTable, TestCaseTable.id == FailureTable.test_case_id)
            .join(StoryTable, StoryTable.id == FailureTable.story_id)
            .outerjoin(UserTable, UserTable.id == FailureTable.assignee_id)
            .where(
                FailureTable.project_id == project_id,
                FailureTable.test_case_id.in_(test_case_ids),
                FailureTable.status.in_(ACTIVE_FAILURE_STATUSES),
            )
            .order_by(FailureTable.created_at, FailureTable.id)
        )
        return [
            PlanFailureBlocker(
                failure_id=failure_id,
                test_case_id=test_case_id,
                code=f"{CASE_CODE_PREFIX}{number}",
                title=title,
                story_jira_key=jira_key,
                status=status,
                assignee_id=assignee_id,
                assignee_name=assignee_name,
                created_at=created_at,
            )
            for (
                failure_id,
                test_case_id,
                number,
                title,
                jira_key,
                status,
                assignee_id,
                assignee_name,
                created_at,
            ) in result
        ]

    async def list_gap_blockers(self, project_id: UUID, story_ids: Collection[UUID]) -> list[PlanGapBlocker]:
        if not story_ids:
            return []
        result = await self._database.get_current_session().execute(
            select(
                GapTable.id,
                GapTable.story_id,
                StoryTable.jira_key,
                GapTable.question,
                GapTable.severity,
                GapTable.assignee_id,
                UserTable.name,
                GapTable.assignee_role,
                GapTable.created_at,
            )
            .join(StoryTable, StoryTable.id == GapTable.story_id)
            .outerjoin(UserTable, UserTable.id == GapTable.assignee_id)
            .where(
                GapTable.project_id == project_id,
                GapTable.story_id.in_(story_ids),
                GapTable.status == GapStatus.OPEN,
            )
            .order_by(GapTable.created_at, GapTable.id)
        )
        return [
            PlanGapBlocker(
                gap_id=gap_id,
                story_id=story_id,
                story_jira_key=jira_key,
                question=question,
                severity=severity,
                assignee_id=assignee_id,
                assignee_name=assignee_name,
                assignee_role=assignee_role,
                created_at=created_at,
            )
            for (
                gap_id,
                story_id,
                jira_key,
                question,
                severity,
                assignee_id,
                assignee_name,
                assignee_role,
                created_at,
            ) in result
        ]

    async def map_environment_names(self, project_id: UUID, environment_ids: Collection[UUID]) -> dict[UUID, str]:
        if not environment_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(EnvironmentTable.id, EnvironmentTable.name).where(
                EnvironmentTable.project_id == project_id, EnvironmentTable.id.in_(environment_ids)
            )
        )
        return dict(result.all())

    async def map_user_names(self, user_ids: Collection[UUID]) -> dict[UUID, str]:
        if not user_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(UserTable.id, UserTable.name).where(UserTable.id.in_(user_ids))
        )
        return dict(result.all())
