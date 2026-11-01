from app.modules.test_data.typing.enums import DataItemKind, ImportAction
from app.shared.common import Entity


class ImportPreviewItem(Entity):
    key: str
    kind: DataItemKind
    value: str | None
    action: ImportAction
