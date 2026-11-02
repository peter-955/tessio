from app.modules.shared_steps import InvalidStepShapeError
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.errors import CaseNotReadyError, UnknownReferenceError
from app.modules.test_cases.typing.constants import DATA_REFERENCE_KIND, FILE_REFERENCE_KIND, PARAMETER_REFERENCE_KIND
from app.modules.test_cases.utils.references import parse_references


def find_unknown_references(
    version: TestCaseVersion, data_keys: frozenset[str], file_keys: frozenset[str]
) -> list[str]:
    references = parse_references(version.preconditions, version.steps, version.data_rows)
    used_data_keys = references.data_keys | set(version.data_keys)
    return sorted(
        [
            *(f"{DATA_REFERENCE_KIND}.{key}" for key in used_data_keys - data_keys),
            *(f"{FILE_REFERENCE_KIND}.{key}" for key in references.file_keys - file_keys),
            *(f"{PARAMETER_REFERENCE_KIND}.{name}" for name in references.parameter_names - set(version.parameters)),
        ]
    )


def require_ready(version: TestCaseVersion, data_keys: frozenset[str], file_keys: frozenset[str]) -> None:
    if not version.steps:
        raise CaseNotReadyError
    if version.parameters and not version.data_rows:
        raise InvalidStepShapeError("Add at least one data row for the parameters, or remove the parameters.")
    unknown_references = find_unknown_references(version, data_keys, file_keys)
    if unknown_references:
        raise UnknownReferenceError(unknown_references)
