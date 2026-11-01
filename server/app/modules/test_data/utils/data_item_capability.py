from collections.abc import Iterable

from app.modules.test_data.typing.enums import DataItemKind
from app.shared.permissions import Capability, ProjectAccess, require


def require_data_item_edit(access: ProjectAccess, kinds: Iterable[DataItemKind]) -> None:
    require(access, Capability.TEST_DATA_EDIT)
    if DataItemKind.SECRET in set(kinds):
        require(access, Capability.SECRET_EDIT)
