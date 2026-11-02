from app.modules.insights.domains.case_share_counts.entity import CaseShareCounts
from app.modules.insights.domains.failing_case.entity import FailingCase
from app.modules.insights.domains.flaky_case.entity import FlakyCase
from app.modules.insights.domains.label_coverage_report.entity import LabelCoverageReport
from app.modules.insights.domains.sprint_coverage.entity import SprintCoverage
from app.modules.insights.domains.token_run.entity import TokenRun
from app.modules.insights.domains.token_usage.entity import TokenUsage
from app.modules.insights.domains.trend_point.entity import TrendPoint
from app.modules.insights.domains.trends.entity import Trends
from app.modules.insights.models.case_share_counts_response import CaseShareCountsResponse
from app.modules.insights.models.executor_count_response import ExecutorCountResponse
from app.modules.insights.models.failing_case_response import FailingCaseResponse
from app.modules.insights.models.flaky_case_response import FlakyCaseResponse
from app.modules.insights.models.label_coverage_report_response import LabelCoverageReportResponse
from app.modules.insights.models.label_coverage_response import LabelCoverageResponse
from app.modules.insights.models.sprint_coverage_response import SprintCoverageResponse
from app.modules.insights.models.sprint_reference_response import SprintReferenceResponse
from app.modules.insights.models.token_run_response import TokenRunResponse
from app.modules.insights.models.token_usage_response import TokenUsageResponse
from app.modules.insights.models.trend_point_response import TrendPointResponse
from app.modules.insights.models.trends_response import TrendsResponse
from app.modules.insights.typing.constants import PASS_RATE_DIGITS
from app.modules.insights.utils.responses import build_coverage_count_response
from app.modules.insights.utils.trend_points import compute_mean


def compute_share(count: int, total: int) -> float | None:
    return None if total == 0 else round(count / total, PASS_RATE_DIGITS)


def build_trend_point_response(point: TrendPoint) -> TrendPointResponse:
    return TrendPointResponse(
        day=point.day,
        sprint=None if point.sprint is None else SprintReferenceResponse.model_validate(point.sprint.model_dump()),
        first_day=point.first_day,
        last_day=point.last_day,
        run_count=point.run_count,
        runs_by_executor=[
            ExecutorCountResponse(executor=count.executor, count=count.count) for count in point.runs_by_executor
        ],
        passed_count=point.passed_count,
        failed_count=point.failed_count,
        blocked_count=point.blocked_count,
        skipped_count=point.skipped_count,
        pass_rate=point.pass_rate,
        failures_opened=point.failures_opened,
        failures_fixed=point.failures_fixed,
        mean_time_to_fix_seconds=point.mean_time_to_fix_seconds,
        gaps_opened=point.gaps_opened,
        gaps_answered=point.gaps_answered,
        mean_gap_answer_seconds=point.mean_gap_answer_seconds,
        open_gap_count=point.open_gap_count,
        median_open_gap_age_seconds=point.median_open_gap_age_seconds,
    )


def build_trends_response(trends: Trends) -> TrendsResponse:
    return TrendsResponse(
        group_by=trends.grouping,
        first_day=trends.day_range.first_day,
        last_day=trends.day_range.last_day,
        executors=trends.executors,
        points=[build_trend_point_response(point) for point in trends.points],
        total=build_trend_point_response(trends.total),
    )


def build_case_share_counts_response(counts: CaseShareCounts) -> CaseShareCountsResponse:
    return CaseShareCountsResponse(
        case_count=counts.case_count,
        ready_count=counts.ready_count,
        passed_count=counts.passed_count,
        ready_share=compute_share(counts.ready_count, counts.case_count),
        passed_share=compute_share(counts.passed_count, counts.case_count),
    )


def build_label_coverage_report_response(report: LabelCoverageReport) -> LabelCoverageReportResponse:
    return LabelCoverageReportResponse(
        labels=[
            LabelCoverageResponse(
                label_id=label.label_id,
                name=label.name,
                color=label.color,
                counts=build_case_share_counts_response(label.counts),
            )
            for label in report.labels
        ],
        unlabelled=build_case_share_counts_response(report.unlabelled),
        total=build_case_share_counts_response(report.total),
    )


def build_failing_case_response(failing_case: FailingCase) -> FailingCaseResponse:
    failing_count = failing_case.failed_count + failing_case.blocked_count
    return FailingCaseResponse(
        test_case_id=failing_case.test_case_id,
        code=failing_case.code,
        title=failing_case.title,
        status=failing_case.status,
        story_jira_key=failing_case.story_jira_key,
        result_count=failing_case.result_count,
        failed_count=failing_case.failed_count,
        blocked_count=failing_case.blocked_count,
        fail_rate=compute_share(failing_count, failing_case.result_count) or 0.0,
        last_failed_at=failing_case.last_failed_at,
        is_flaky=failing_case.is_flaky,
        is_quarantined=failing_case.is_quarantined,
    )


def build_flaky_case_response(flaky_case: FlakyCase) -> FlakyCaseResponse:
    return FlakyCaseResponse(
        test_case_id=flaky_case.test_case_id,
        code=flaky_case.code,
        title=flaky_case.title,
        status=flaky_case.status,
        story_jira_key=flaky_case.story_jira_key,
        flaky_score=flaky_case.flaky_score,
        is_flaky=flaky_case.flaky_since is not None,
        flaky_since=flaky_case.flaky_since,
        is_disagreeing=flaky_case.disagreed_at is not None,
        disagreed_at=flaky_case.disagreed_at,
        is_quarantined=flaky_case.quarantined_at is not None,
        quarantined_at=flaky_case.quarantined_at,
    )


def build_token_run_response(run: TokenRun) -> TokenRunResponse:
    return TokenRunResponse(
        run_id=run.run_id,
        started_at=run.started_at,
        executor=run.executor,
        story_jira_key=run.story_jira_key,
        test_suite_name=run.test_suite_name,
        case_count=run.case_count,
        input_tokens=run.input_tokens,
        cache_creation_input_tokens=run.cache_creation_input_tokens,
        cache_read_input_tokens=run.cache_read_input_tokens,
        output_tokens=run.output_tokens,
        total_tokens=run.total_tokens,
        tokens_per_case=compute_mean(run.total_tokens, run.case_count),
        is_cut=run.is_cut,
    )


def build_token_usage_response(usage: TokenUsage) -> TokenUsageResponse:
    return TokenUsageResponse(
        first_day=usage.day_range.first_day,
        last_day=usage.day_range.last_day,
        runs=[build_token_run_response(run) for run in usage.runs],
        total_tokens=usage.total_tokens,
        mean_tokens_per_run=usage.mean_tokens_per_run,
        mean_tokens_per_case=usage.mean_tokens_per_case,
    )


def build_sprint_coverage_response(sprint_coverage: SprintCoverage) -> SprintCoverageResponse:
    return SprintCoverageResponse(
        sprint=SprintReferenceResponse.model_validate(sprint_coverage.sprint.model_dump()),
        story_count=sprint_coverage.story_count,
        coverage=build_coverage_count_response(sprint_coverage.coverage),
    )
