from app.modules.failures.typing.enums import FailureStatus

ACTIVE_FAILURE_STATUSES: tuple[FailureStatus, ...] = (
    FailureStatus.OPEN,
    FailureStatus.REOPENED,
    FailureStatus.FIXED,
)
FAILURE_TO_FIX_STATUSES: tuple[FailureStatus, ...] = (FailureStatus.OPEN, FailureStatus.REOPENED)
