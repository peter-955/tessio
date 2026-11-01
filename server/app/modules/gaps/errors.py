from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class GapNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Gap not found.")


class GapNotOpenError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.GAP_NOT_OPEN, "This gap is already resolved.")


class GapNotResolvedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_STATUS_TRANSITION, "Only a resolved gap can be reopened.")


class AssigneeNotActiveMemberError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.ASSIGNEE_NOT_ACTIVE_MEMBER, "Pick an active project member who can answer gaps.")


class UnknownGapTargetError(TessioError):
    def __init__(self, target_ref: str) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, f"{target_ref} is not on this story.")


class OpenGapsBlockRunError(TessioError):
    def __init__(self, count: int) -> None:
        super().__init__(ErrorCode.OPEN_GAPS_BLOCK_RUN, f"{count} open gaps block runs on this story.")
