from app.modules.runs import ResultStatus

FAILING_RESULT_STATUSES: frozenset[ResultStatus] = frozenset({ResultStatus.FAILED, ResultStatus.BLOCKED})
