from collections.abc import Collection, Mapping, Sequence

from app.modules.shared_steps import (
    MAX_EXPANDED_CASE_STEPS,
    CurrentSharedStep,
    ExpandedCaseTooLongError,
    InvalidStepShapeError,
    UnknownSharedStepError,
    count_expanded_steps,
)
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.errors import SecretInDataRowError
from app.modules.test_cases.typing.constants import MAX_DATA_ROWS, MAX_PARAMETERS
from app.shared.masking import SecretMasker


def require_data_table(parameters: Sequence[str], data_rows: Sequence[Mapping[str, str]]) -> None:
    if len(parameters) > MAX_PARAMETERS:
        raise InvalidStepShapeError(f"A case can have at most {MAX_PARAMETERS} parameters.")
    if len(data_rows) > MAX_DATA_ROWS:
        raise InvalidStepShapeError(f"A case can have at most {MAX_DATA_ROWS} data rows.")
    if len({name.casefold() for name in parameters}) != len(parameters):
        raise InvalidStepShapeError("Each parameter needs its own name.")
    if data_rows and not parameters:
        raise InvalidStepShapeError("Add the parameters before the data rows.")
    if parameters and not data_rows:
        raise InvalidStepShapeError("Add at least one data row for the parameters, or remove the parameters.")
    expected_names = set(parameters)
    for row_number, row in enumerate(data_rows, start=1):
        if set(row) != expected_names:
            raise InvalidStepShapeError(f"Data row {row_number} needs exactly one value for each parameter.")


def require_known_shared_steps(
    steps: Sequence[TestStep], shared_steps: Mapping[str, CurrentSharedStep], kept_keys: Collection[str]
) -> None:
    unknown_keys = [
        key
        for key in dict.fromkeys(step.shared_step_key for step in steps if step.is_shared_step_reference)
        if key is not None
        and (key not in shared_steps or (shared_steps[key].shared_step.is_archived and key not in kept_keys))
    ]
    if unknown_keys:
        raise UnknownSharedStepError(unknown_keys)


def require_expanded_step_limit(steps: Sequence[TestStep], shared_steps: Mapping[str, CurrentSharedStep]) -> None:
    action_counts = {key: len(current.version.steps) for key, current in shared_steps.items()}
    step_count = count_expanded_steps(
        (step.shared_step_key if step.is_shared_step_reference else None for step in steps), action_counts
    )
    if step_count > MAX_EXPANDED_CASE_STEPS:
        raise ExpandedCaseTooLongError(step_count)


def require_no_secret_values(data_rows: Sequence[Mapping[str, str]], secret_values: Collection[str]) -> None:
    masker = SecretMasker(secret_values)
    for row_number, row in enumerate(data_rows, start=1):
        if any(masker.mask(value) != value for value in row.values()):
            raise SecretInDataRowError(row_number)
