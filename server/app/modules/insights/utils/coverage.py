from collections import defaultdict
from collections.abc import Sequence
from uuid import UUID

from app.modules.insights.domains.coverage_count.entity import CoverageCount
from app.modules.insights.domains.criterion_trace.entity import CriterionTrace
from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.domains.traced_criterion.entity import TracedCriterion
from app.modules.insights.utils.criterion_status import resolve_criterion_status
from app.modules.runs import CriterionStatus
from app.modules.test_cases import TestCaseStatus


def build_criterion_traces(criteria: list[TracedCriterion], cases: list[TracedCase]) -> list[CriterionTrace]:
    ordered_cases = sorted(
        (case for case in cases if case.status is not TestCaseStatus.DEPRECATED), key=lambda case: case.number
    )
    ordered_criteria = sorted(criteria, key=lambda criterion: (not criterion.is_active, criterion.position))
    traces: list[CriterionTrace] = []
    for criterion in ordered_criteria:
        linked = [case for case in ordered_cases if criterion.id in case.criterion_ids]
        traces.append(
            CriterionTrace(
                criterion=criterion,
                status=resolve_criterion_status(linked),
                linked_case_ids=[case.id for case in linked],
            )
        )
    return traces


def count_coverage(traces: Sequence[CriterionTrace]) -> CoverageCount:
    statuses = [trace.status for trace in traces if trace.criterion.is_active]
    uncovered_count = statuses.count(CriterionStatus.UNCOVERED)
    return CoverageCount(
        criterion_count=len(statuses),
        covered_count=len(statuses) - uncovered_count,
        passed_count=statuses.count(CriterionStatus.PASSED),
        failed_count=statuses.count(CriterionStatus.FAILED),
        blocked_count=statuses.count(CriterionStatus.BLOCKED),
        not_run_count=statuses.count(CriterionStatus.NOT_RUN),
        uncovered_count=uncovered_count,
    )


def count_coverage_by_story(traces: Sequence[CriterionTrace]) -> dict[UUID, CoverageCount]:
    traces_by_story: dict[UUID, list[CriterionTrace]] = defaultdict(list)
    for trace in traces:
        traces_by_story[trace.criterion.story_id].append(trace)
    return {story_id: count_coverage(story_traces) for story_id, story_traces in traces_by_story.items()}
