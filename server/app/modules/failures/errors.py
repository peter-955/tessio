from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class FailureNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Failure not found.")


class InvalidFailureTransitionError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_STATUS_TRANSITION, "This failure status change is not allowed.")


class FailureClosedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_STATUS_TRANSITION, "A verified failure cannot be reassigned.")


class AssigneeNotActiveMemberError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.ASSIGNEE_NOT_ACTIVE_MEMBER, "Pick an active project member.")


class InvalidFailureFilterError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Use either assigneeId or unassigned, not both.")
