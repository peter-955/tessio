import re
from collections.abc import Sequence

from app.modules.test_cases.domains.case_references.entity import CaseReferences
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.constants import DATA_REFERENCE_KIND, REFERENCE_PATTERN


def parse_references(preconditions: str | None, steps: Sequence[TestStep]) -> CaseReferences:
    texts = [preconditions, *(text for step in steps for text in (step.action, step.expected))]
    data_keys: set[str] = set()
    file_keys: set[str] = set()
    for text in texts:
        if text is None:
            continue
        for kind, key in re.findall(REFERENCE_PATTERN, text):
            (data_keys if kind == DATA_REFERENCE_KIND else file_keys).add(key)
    return CaseReferences(data_keys=frozenset(data_keys), file_keys=frozenset(file_keys))
