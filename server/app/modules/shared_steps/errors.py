from app.modules.shared_steps.typing.constants import MAX_EXPANDED_CASE_STEPS
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class SharedStepNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Shared step not found.")


class SharedStepKeyAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SHARED_STEP_KEY_ALREADY_USED, "Another shared step in this project has this key.")


class InvalidSharedStepKeyError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.INVALID_REQUEST,
            "A shared step key starts with a letter and uses only letters, digits and _ (at most 64).",
        )


class SharedStepVersionConflictError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "Someone saved a newer version. Reload and try again.")


class UnknownSharedStepError(TessioError):
    def __init__(self, keys: list[str]) -> None:
        self.keys = keys
        named_keys = ", ".join(keys)
        super().__init__(
            ErrorCode.UNKNOWN_SHARED_STEP, f"These shared steps do not exist or are archived: {named_keys}."
        )


class InvalidStepShapeError(TessioError):
    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.INVALID_STEP_SHAPE, message)


class ExpandedCaseTooLongError(TessioError):
    def __init__(self, step_count: int) -> None:
        self.step_count = step_count
        super().__init__(
            ErrorCode.INVALID_STEP_SHAPE,
            f"With its shared steps expanded, this case has {step_count} steps. "
            f"A case can have at most {MAX_EXPANDED_CASE_STEPS} steps once its shared steps are expanded.",
        )


class SharedStepMakesCaseTooLongError(TessioError):
    def __init__(self, case_codes: list[str]) -> None:
        self.case_codes = case_codes
        named_codes = ", ".join(case_codes)
        super().__init__(
            ErrorCode.INVALID_STEP_SHAPE,
            f"With these steps, these cases would have more than {MAX_EXPANDED_CASE_STEPS} steps "
            f"once their shared steps are expanded: {named_codes}.",
        )
