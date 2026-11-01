from app.modules.test_cases.domains.case_import_preview_item.entity import CaseImportPreviewItem
from app.modules.test_cases.domains.case_import_skip.entity import CaseImportSkip
from app.modules.test_cases.typing.enums import CaseImportFormat
from app.shared.common import Entity


class CaseImportPreview(Entity):
    format: CaseImportFormat
    items: list[CaseImportPreviewItem]
    skipped: list[CaseImportSkip]
