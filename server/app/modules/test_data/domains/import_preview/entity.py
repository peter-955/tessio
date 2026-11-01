from app.modules.test_data.domains.import_preview_item.entity import ImportPreviewItem
from app.modules.test_data.domains.import_skip.entity import ImportSkip
from app.modules.test_data.typing.enums import ImportFormat
from app.shared.common import Entity


class ImportPreview(Entity):
    format: ImportFormat
    items: list[ImportPreviewItem]
    skipped: list[ImportSkip]
