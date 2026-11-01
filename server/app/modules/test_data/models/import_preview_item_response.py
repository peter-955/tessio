from app.modules.test_data.typing.enums import DataItemKind, ImportAction
from app.shared.common import WireModel


class ImportPreviewItemResponse(WireModel):
    key: str
    kind: DataItemKind
    value: str | None
    action: ImportAction
