from app.modules.test_cases.domains.imported_case_code.entity import ImportedCaseCode
from app.shared.common import Entity


class CaseImportResult(Entity):
    created: list[ImportedCaseCode]
