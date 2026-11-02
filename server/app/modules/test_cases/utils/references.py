import re
from collections.abc import Iterable, Sequence

from app.modules.test_cases.domains.case_references.entity import CaseReferences
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.constants import DATA_REFERENCE_KIND, PARAMETER_REFERENCE_KIND, REFERENCE_PATTERN


def parse_references(
    preconditions: str | None, steps: Sequence[TestStep], data_rows: Sequence[dict[str, str]] = ()
) -> CaseReferences:
    data_keys: set[str] = set()
    file_keys: set[str] = set()
    parameter_names: set[str] = set()
    keys_by_kind = {DATA_REFERENCE_KIND: data_keys, PARAMETER_REFERENCE_KIND: parameter_names}
    for text in collect_case_texts(preconditions, steps, data_rows):
        for kind, key in re.findall(REFERENCE_PATTERN, text):
            keys_by_kind.get(kind, file_keys).add(key)
    return CaseReferences(
        data_keys=frozenset(data_keys), file_keys=frozenset(file_keys), parameter_names=frozenset(parameter_names)
    )


def collect_case_texts(
    preconditions: str | None, steps: Sequence[TestStep], data_rows: Sequence[dict[str, str]]
) -> Iterable[str]:
    texts = [
        preconditions,
        *(text for step in steps for text in (step.action, step.expected)),
        *(value for row in data_rows for value in row.values()),
    ]
    return [text for text in texts if text]
