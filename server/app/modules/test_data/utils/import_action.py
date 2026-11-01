from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.typing.enums import DataItemKind, ImportAction
from app.modules.test_data.utils.data_item_value import read_data_item_value
from app.shared.crypto import SecretCipher


def resolve_import_action(
    existing_item: DataItem | None, kind: DataItemKind, value: str, secret_cipher: SecretCipher
) -> ImportAction:
    if existing_item is None:
        return ImportAction.CREATE
    if existing_item.kind is kind and read_data_item_value(existing_item, secret_cipher) == value:
        return ImportAction.UNCHANGED
    return ImportAction.UPDATE
