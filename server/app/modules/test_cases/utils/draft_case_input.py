from collections.abc import Sequence

from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.models.draft_case_tool_input import DraftCaseToolInput
from app.modules.test_cases.utils.case_import_cells import parse_criterion_codes


def normalize_criterion_codes(codes: Sequence[str]) -> list[str]:
    normalized = [
        code
        for raw_code in codes
        if raw_code.strip()
        for code in (parse_criterion_codes(raw_code) or [raw_code.strip().upper()])
    ]
    return list(dict.fromkeys(normalized))


def build_imported_case(draft_case: DraftCaseToolInput) -> ImportedCase:
    return ImportedCase(
        location=draft_case.source,
        story_key=draft_case.story_key.upper(),
        title=draft_case.title,
        priority=draft_case.priority,
        business_value=draft_case.business_value or None,
        preconditions=draft_case.preconditions or None,
        steps=[
            TestStep(order=order, action=step.action, expected=step.expected or None)
            for order, step in enumerate(draft_case.steps, 1)
        ],
        criterion_codes=normalize_criterion_codes(draft_case.criterion_codes),
    )
