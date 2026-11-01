from app.modules.test_cases.domains.case_import_skip.entity import CaseImportSkip
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.typing.enums import CaseImportFormat
from app.shared.common import Entity


class ParsedCaseImport(Entity):
    format: CaseImportFormat
    cases: list[ImportedCase]
    skipped: list[CaseImportSkip]
