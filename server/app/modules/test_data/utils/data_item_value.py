from datetime import datetime
from uuid import UUID

from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.typing.enums import DataItemKind
from app.shared.crypto import SecretCipher


def apply_data_item_value(item: DataItem, kind: DataItemKind, value: str, secret_cipher: SecretCipher) -> DataItem:
    if kind is DataItemKind.SECRET:
        return item.model_copy(
            update={"kind": kind, "value": None, "value_encrypted": secret_cipher.encrypt(value.encode())}
        )
    return item.model_copy(update={"kind": kind, "value": value, "value_encrypted": None})


def build_data_item(
    item_id: UUID,
    project_id: UUID,
    environment_id: UUID | None,
    key: str,
    kind: DataItemKind,
    value: str,
    created_at: datetime,
    secret_cipher: SecretCipher,
) -> DataItem:
    item = DataItem(
        id=item_id,
        project_id=project_id,
        environment_id=environment_id,
        key=key,
        kind=kind,
        value=None,
        value_encrypted=None,
        created_at=created_at,
    )
    return apply_data_item_value(item, kind, value, secret_cipher)


def read_data_item_value(item: DataItem, secret_cipher: SecretCipher) -> str | None:
    if item.value_encrypted is None:
        return item.value
    return secret_cipher.decrypt(item.value_encrypted).decode()
