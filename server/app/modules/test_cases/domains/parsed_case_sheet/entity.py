from app.modules.test_cases.domains.case_import_skip.entity import CaseImportSkip
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.shared.common import Entity


class ParsedCaseSheet(Entity):
    cases: list[ImportedCase]
    skipped: list[CaseImportSkip]
    row_count: int
