from collections.abc import Collection

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.typing.enums import ResultStatus, RunAbortReason, RunStatus


def decide_run_status(result_statuses: Collection[ResultStatus]) -> RunStatus:
    if not result_statuses:
        return RunStatus.ABORTED
    if any(status in {ResultStatus.FAILED, ResultStatus.BLOCKED} for status in result_statuses):
        return RunStatus.FAILED
    return RunStatus.PASSED


def resolve_finished_status(case_results: Collection[CaseResult]) -> tuple[RunStatus, RunAbortReason | None]:
    status = decide_run_status([case_result.status for case_result in case_results])
    return status, RunAbortReason.NO_RESULTS if status is RunStatus.ABORTED else None
