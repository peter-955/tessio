from uuid import UUID

from app.modules.plans.domains.plan_case_progress.entity import PlanCaseProgress
from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.plan_item_view.entity import PlanItemView
from app.modules.plans.domains.plan_progress.entity import PlanProgress
from app.modules.plans.domains.plan_progress_counts.entity import PlanProgressCounts
from app.modules.plans.domains.plan_summary.entity import PlanSummary
from app.modules.plans.models.plan_case_response import PlanCaseResponse
from app.modules.plans.models.plan_detail_response import PlanDetailResponse
from app.modules.plans.models.plan_failure_response import PlanFailureResponse
from app.modules.plans.models.plan_gap_response import PlanGapResponse
from app.modules.plans.models.plan_item_response import PlanItemResponse
from app.modules.plans.models.plan_latest_result_response import PlanLatestResultResponse
from app.modules.plans.models.plan_progress_counts_response import PlanProgressCountsResponse
from app.modules.plans.models.plan_progress_response import PlanProgressResponse
from app.modules.plans.models.plan_summary_response import PlanSummaryResponse


def build_plan_counts_response(counts: PlanProgressCounts) -> PlanProgressCountsResponse:
    return PlanProgressCountsResponse.model_validate(counts.model_dump())


def build_plan_summary_response(summary: PlanSummary) -> PlanSummaryResponse:
    plan = summary.plan
    return PlanSummaryResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        status=plan.status,
        target_date=plan.target_date,
        environment_id=plan.environment_id,
        environment_name=summary.environment_name,
        item_count=summary.item_count,
        counts=build_plan_counts_response(summary.counts),
        created_by=plan.created_by,
        created_at=plan.created_at,
        signed_off_at=plan.signed_off_at,
        closed_at=plan.closed_at,
    )


def build_plan_item_response(item: PlanItemView) -> PlanItemResponse:
    return PlanItemResponse(
        position=item.position,
        kind=item.kind,
        suite_id=item.test_suite_id,
        story_id=item.story_id,
        name=item.name,
        story_jira_key=item.story_jira_key,
        archived_at=item.archived_at,
        case_count=item.case_count,
    )


def build_plan_case_response(progress: PlanCaseProgress) -> PlanCaseResponse:
    return PlanCaseResponse(
        **progress.case.model_dump(),
        latest_result=None
        if progress.latest_result is None
        else PlanLatestResultResponse.model_validate(progress.latest_result.model_dump()),
        active_failure_id=None if progress.active_failure is None else progress.active_failure.failure_id,
        active_failure_status=None if progress.active_failure is None else progress.active_failure.status,
    )


def build_plan_progress_response(progress: PlanProgress) -> PlanProgressResponse:
    return PlanProgressResponse(
        counts=build_plan_counts_response(progress.counts),
        cases=[build_plan_case_response(case) for case in progress.cases],
        failures=[PlanFailureResponse.model_validate(failure.model_dump()) for failure in progress.failures],
        gaps=[PlanGapResponse.model_validate(gap.model_dump()) for gap in progress.gaps],
    )


def find_user_name(detail: PlanDetail, user_id: UUID | None) -> str | None:
    return None if user_id is None else detail.user_names.get(user_id)


def build_plan_detail_response(detail: PlanDetail) -> PlanDetailResponse:
    plan = detail.plan
    return PlanDetailResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        status=plan.status,
        target_date=plan.target_date,
        environment_id=plan.environment_id,
        environment_name=detail.environment_name,
        created_by=plan.created_by,
        created_by_name=find_user_name(detail, plan.created_by),
        created_at=plan.created_at,
        signed_off_by=plan.signed_off_by,
        signed_off_by_name=find_user_name(detail, plan.signed_off_by),
        signed_off_at=plan.signed_off_at,
        closed_by=plan.closed_by,
        closed_by_name=find_user_name(detail, plan.closed_by),
        closed_at=plan.closed_at,
        items=[build_plan_item_response(item) for item in detail.items],
        progress=build_plan_progress_response(detail.progress),
    )
