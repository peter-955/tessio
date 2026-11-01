from app.modules.test_data.typing.enums import DataItemKind
from app.shared.common import Entity


class ImportChoice(Entity):
    key: str
    kind: DataItemKind
