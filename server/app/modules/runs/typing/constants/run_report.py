from app.modules.runs.typing.enums import ResultStatus

FAILING_RESULT_STATUSES = frozenset({ResultStatus.FAILED, ResultStatus.BLOCKED})
WORST_FIRST_RESULT_STATUSES = (ResultStatus.FAILED, ResultStatus.BLOCKED, ResultStatus.PASSED, ResultStatus.SKIPPED)
