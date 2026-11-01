from app.modules.runs.typing.enums import ResultStatus

FAILING_RESULT_STATUSES = frozenset({ResultStatus.FAILED, ResultStatus.BLOCKED})
