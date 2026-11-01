from app.modules.test_cases.models.case_import_preview_item_response import CaseImportPreviewItemResponse
from app.modules.test_cases.models.case_import_skip_response import CaseImportSkipResponse
from app.modules.test_cases.typing.enums import CaseImportFormat
from app.shared.common import WireModel


class CaseImportPreviewResponse(WireModel):
    format: CaseImportFormat
    items: list[CaseImportPreviewItemResponse]
    skipped: list[CaseImportSkipResponse]
