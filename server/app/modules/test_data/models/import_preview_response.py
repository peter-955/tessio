from app.modules.test_data.models.import_preview_item_response import ImportPreviewItemResponse
from app.modules.test_data.models.import_skip_response import ImportSkipResponse
from app.modules.test_data.typing.enums import ImportFormat
from app.shared.common import WireModel


class ImportPreviewResponse(WireModel):
    format: ImportFormat
    items: list[ImportPreviewItemResponse]
    skipped: list[ImportSkipResponse]
