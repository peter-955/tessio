from collections.abc import Iterable

from app.modules.plans.domains.plan_case_progress.entity import PlanCaseProgress
from app.modules.plans.domains.plan_failure_blocker.entity import PlanFailureBlocker
from app.modules.plans.domains.plan_progress.entity import PlanProgress
from app.modules.plans.domains.plan_progress_counts.entity import PlanProgressCounts
from app.modules.plans.domains.plan_progress_window.entity import PlanProgressWindow
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.runs import ResultStatus


def build_progress_window(plan: TestPlan) -> PlanProgressWindow:
    return PlanProgressWindow(
        project_id=plan.project_id,
        since=plan.created_at,
        until=plan.progress_until,
        environment_id=plan.environment_id,
    )


def build_progress_counts(statuses: Iterable[ResultStatus | None]) -> PlanProgressCounts:
    listed = list(statuses)
    return PlanProgressCounts(
        total=len(listed),
        passed=listed.count(ResultStatus.PASSED),
        failed=listed.count(ResultStatus.FAILED),
        blocked=listed.count(ResultStatus.BLOCKED),
        skipped=listed.count(ResultStatus.SKIPPED),
        not_run=listed.count(None),
    )


async def load_plan_counts(plan_view_reader: PlanViewReader, plan: TestPlan) -> PlanProgressCounts:
    cases = await plan_view_reader.list_plan_cases(plan.id)
    latest_results = await plan_view_reader.map_latest_results(
        [case.test_case_id for case in cases], build_progress_window(plan)
    )
    return build_progress_counts(
        None if latest_results.get(case.test_case_id) is None else latest_results[case.test_case_id].status
        for case in cases
    )


async def list_active_plan_failures(plan_view_reader: PlanViewReader, plan: TestPlan) -> list[PlanFailureBlocker]:
    cases = await plan_view_reader.list_plan_cases(plan.id)
    return await plan_view_reader.list_failure_blockers(plan.project_id, [case.test_case_id for case in cases])


async def load_plan_progress(plan_view_reader: PlanViewReader, plan: TestPlan) -> PlanProgress:
    cases = await plan_view_reader.list_plan_cases(plan.id)
    case_ids = [case.test_case_id for case in cases]
    latest_results = await plan_view_reader.map_latest_results(case_ids, build_progress_window(plan))
    failures = await plan_view_reader.list_failure_blockers(plan.project_id, case_ids)
    story_ids = {case.story_id for case in cases} | await plan_view_reader.list_plan_story_ids(plan.id)
    gaps = await plan_view_reader.list_gap_blockers(plan.project_id, story_ids)
    failure_by_case_id = {failure.test_case_id: failure for failure in failures}
    case_progress = [
        PlanCaseProgress(
            case=case,
            latest_result=latest_results.get(case.test_case_id),
            active_failure=failure_by_case_id.get(case.test_case_id),
        )
        for case in cases
    ]
    return PlanProgress(
        counts=build_progress_counts(
            None if progress.latest_result is None else progress.latest_result.status for progress in case_progress
        ),
        cases=case_progress,
        failures=failures,
        gaps=gaps,
    )
