from app.modules.test_data import DataItemKind
from app.shared.common import Entity


class RunDataValue(Entity):
    key: str
    kind: DataItemKind
    value: str | None
