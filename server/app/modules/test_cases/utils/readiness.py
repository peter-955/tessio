from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.errors import CaseNotReadyError, UnknownReferenceError
from app.modules.test_cases.typing.constants import DATA_REFERENCE_KIND, FILE_REFERENCE_KIND
from app.modules.test_cases.utils.references import parse_references


def find_unknown_references(
    version: TestCaseVersion, data_keys: frozenset[str], file_keys: frozenset[str]
) -> list[str]:
    references = parse_references(version.preconditions, version.steps)
    return sorted(
        [
            *(f"{DATA_REFERENCE_KIND}.{key}" for key in references.data_keys - data_keys),
            *(f"{FILE_REFERENCE_KIND}.{key}" for key in references.file_keys - file_keys),
        ]
    )


def require_ready(version: TestCaseVersion, data_keys: frozenset[str], file_keys: frozenset[str]) -> None:
    if not version.steps:
        raise CaseNotReadyError
    unknown_references = find_unknown_references(version, data_keys, file_keys)
    if unknown_references:
        raise UnknownReferenceError(unknown_references)
