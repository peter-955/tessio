from app.modules.insights.domains.case_latest_result.entity import CaseLatestResult
from app.modules.insights.domains.coverage_count.entity import CoverageCount
from app.modules.insights.domains.criterion_trace.entity import CriterionTrace
from app.modules.insights.domains.dashboard_summary.entity import DashboardSummary
from app.modules.insights.domains.latest_result.entity import LatestResult
from app.modules.insights.domains.my_work.entity import MyWork
from app.modules.insights.domains.run_reference.entity import RunReference
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.story_progress.entity import StoryProgress
from app.modules.insights.domains.traceability.entity import Traceability
from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.models.case_latest_result_response import CaseLatestResultResponse
from app.modules.insights.models.coverage_count_response import CoverageCountResponse
from app.modules.insights.models.criterion_trace_response import CriterionTraceResponse
from app.modules.insights.models.dashboard_response import DashboardResponse
from app.modules.insights.models.draft_case_list_response import DraftCaseListResponse
from app.modules.insights.models.failure_to_fix_list_response import FailureToFixListResponse
from app.modules.insights.models.gap_to_answer_list_response import GapToAnswerListResponse
from app.modules.insights.models.latest_result_response import LatestResultResponse
from app.modules.insights.models.my_work_response import MyWorkResponse
from app.modules.insights.models.run_reference_response import RunReferenceResponse
from app.modules.insights.models.sprint_reference_response import SprintReferenceResponse
from app.modules.insights.models.story_progress_response import StoryProgressResponse
from app.modules.insights.models.test_status_counts_response import TestStatusCountsResponse
from app.modules.insights.models.traceability_response import TraceabilityResponse
from app.modules.insights.models.traced_case_response import TracedCaseResponse
from app.modules.insights.models.uncovered_criterion_list_response import UncoveredCriterionListResponse


def build_latest_result_response(latest_result: LatestResult | None) -> LatestResultResponse | None:
    return None if latest_result is None else LatestResultResponse.model_validate(latest_result.model_dump())


def build_coverage_count_response(coverage: CoverageCount) -> CoverageCountResponse:
    return CoverageCountResponse.model_validate(coverage.model_dump())


def build_criterion_trace_response(trace: CriterionTrace) -> CriterionTraceResponse:
    criterion = trace.criterion
    return CriterionTraceResponse(
        id=criterion.id,
        code=criterion.code,
        position=criterion.position,
        text=criterion.text,
        removed_at=criterion.removed_at,
        status=trace.status,
        linked_case_ids=trace.linked_case_ids,
    )


def build_traced_case_response(case: TracedCase) -> TracedCaseResponse:
    return TracedCaseResponse(
        id=case.id,
        code=case.code,
        title=case.title,
        status=case.status,
        priority=case.priority,
        needs_review=case.is_needing_review,
        criterion_ids=sorted(case.criterion_ids),
        latest_result=build_latest_result_response(case.latest_result),
    )


def build_traceability_response(traceability: Traceability) -> TraceabilityResponse:
    return TraceabilityResponse(
        story_id=traceability.story.id,
        jira_key=traceability.story.jira_key,
        coverage=build_coverage_count_response(traceability.coverage),
        criteria=[build_criterion_trace_response(trace) for trace in traceability.criteria],
        cases=[build_traced_case_response(case) for case in traceability.cases],
    )


def build_run_reference_response(run: RunReference | None) -> RunReferenceResponse | None:
    return None if run is None else RunReferenceResponse.model_validate(run.model_dump())


def build_story_progress_response(progress: StoryProgress) -> StoryProgressResponse:
    return StoryProgressResponse(
        story_id=progress.story_id,
        jira_key=progress.jira_key,
        coverage=build_coverage_count_response(progress.coverage),
        open_gap_count=progress.open_gap_count,
        active_failure_count=progress.active_failure_count,
        last_run=build_run_reference_response(progress.last_run),
    )


def build_case_latest_result_response(case_result: CaseLatestResult) -> CaseLatestResultResponse:
    return CaseLatestResultResponse(
        case_id=case_result.case_id,
        code=case_result.code,
        story_id=case_result.story_id,
        latest_result=build_latest_result_response(case_result.latest_result),
    )


def build_sprint_reference_response(sprint: SprintReference | None) -> SprintReferenceResponse | None:
    return None if sprint is None else SprintReferenceResponse.model_validate(sprint.model_dump())


def build_dashboard_response(summary: DashboardSummary) -> DashboardResponse:
    return DashboardResponse(
        sprint=build_sprint_reference_response(summary.sprint),
        story_count=summary.story_count,
        test_status_counts=TestStatusCountsResponse.model_validate(summary.test_status_counts.model_dump()),
        open_gap_count=summary.open_gap_count,
        active_failure_count=summary.active_failure_count,
        coverage=build_coverage_count_response(summary.coverage),
    )


def build_my_work_response(my_work: MyWork) -> MyWorkResponse:
    return MyWorkResponse(
        role=my_work.role,
        sections=my_work.sections,
        sprint=build_sprint_reference_response(my_work.sprint),
        uncovered_criteria=UncoveredCriterionListResponse.model_validate(my_work.uncovered_criteria.model_dump()),
        draft_cases=DraftCaseListResponse.model_validate(my_work.draft_cases.model_dump()),
        failures_to_fix=FailureToFixListResponse.model_validate(my_work.failures_to_fix.model_dump()),
        gaps_to_answer=GapToAnswerListResponse.model_validate(my_work.gaps_to_answer.model_dump()),
        unassigned_failure_count=my_work.unassigned_failure_count,
    )
