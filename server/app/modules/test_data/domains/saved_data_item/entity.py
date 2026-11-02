from app.modules.test_data.typing.enums import DataSaveAction
from app.shared.common import Entity


class SavedDataItem(Entity):
    action: DataSaveAction
    overridden_in: list[str]
