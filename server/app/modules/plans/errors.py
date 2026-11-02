from app.modules.plans.typing.constants import MAX_PLAN_ITEMS
from app.modules.plans.typing.enums import PlanStatus
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode

PLAN_NOT_OPEN_MESSAGES = {
    PlanStatus.SIGNED_OFF: "This plan is signed off, so it can no longer change.",
    PlanStatus.CLOSED: "This plan is closed, so it can no longer change.",
}


class PlanNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Test plan not found.")


class PlanNotOpenError(TessioError):
    def __init__(self, status: PlanStatus) -> None:
        super().__init__(ErrorCode.PLAN_NOT_OPEN, PLAN_NOT_OPEN_MESSAGES.get(status, "This plan is not open."))


class PlanFailuresActiveError(TessioError):
    def __init__(self, failure_count: int) -> None:
        noun = "failure" if failure_count == 1 else "failures"
        super().__init__(
            ErrorCode.PLAN_FAILURES_ACTIVE,
            f"Resolve the {failure_count} active {noun} on this plan's cases before signing it off.",
        )


class UnknownPlanItemError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "Use only suites and stories of this project.")


class DuplicatePlanItemError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "List each suite and story only once.")


class TooManyPlanItemsError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, f"A plan holds at most {MAX_PLAN_ITEMS} suites and stories.")


class UnknownPlanEnvironmentError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "Pick an active environment of this project.")
