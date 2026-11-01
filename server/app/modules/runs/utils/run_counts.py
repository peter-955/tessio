from collections import Counter
from collections.abc import Collection

from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.typing.enums import ResultStatus


def build_run_counts(total: int, result_statuses: Collection[ResultStatus]) -> RunCounts:
    status_counts = Counter(result_statuses)
    return RunCounts(
        total=total,
        passed=status_counts[ResultStatus.PASSED],
        failed=status_counts[ResultStatus.FAILED],
        blocked=status_counts[ResultStatus.BLOCKED],
        skipped=status_counts[ResultStatus.SKIPPED],
        not_reported=max(total - len(result_statuses), 0),
    )
