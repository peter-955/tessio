from app.modules.test_cases.models.imported_case_code_response import ImportedCaseCodeResponse
from app.shared.common import WireModel


class CaseImportResultResponse(WireModel):
    created: list[ImportedCaseCodeResponse]
