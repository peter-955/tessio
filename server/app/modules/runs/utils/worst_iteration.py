from collections.abc import Iterable
from uuid import UUID

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.typing.constants.run_report import WORST_FIRST_RESULT_STATUSES
from app.modules.runs.typing.enums import ResultStatus


def rank_result_status(status: ResultStatus) -> int:
    return WORST_FIRST_RESULT_STATUSES.index(status)


def is_worse_result(candidate: CaseResult, current: CaseResult) -> bool:
    candidate_rank = (rank_result_status(candidate.status), candidate.iteration)
    current_rank = (rank_result_status(current.status), current.iteration)
    return candidate_rank < current_rank


def select_worst_results(case_results: Iterable[CaseResult]) -> dict[UUID, CaseResult]:
    worst_by_case_id: dict[UUID, CaseResult] = {}
    for case_result in case_results:
        current = worst_by_case_id.get(case_result.test_case_id)
        if current is None or is_worse_result(case_result, current):
            worst_by_case_id[case_result.test_case_id] = case_result
    return worst_by_case_id


def is_new_case_outcome(case_result: CaseResult, earlier_results: Iterable[CaseResult]) -> bool:
    new_rank = rank_result_status(case_result.status)
    return all(new_rank < rank_result_status(earlier.status) for earlier in earlier_results)
