from app.modules.test_data import DataItemKind
from app.shared.common import WireModel


class RunDataValueResponse(WireModel):
    key: str
    kind: DataItemKind
    value: str | None
