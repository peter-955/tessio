from collections.abc import Collection
from uuid import UUID

from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.utils.effective_data_items import select_effective_items
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher


class SecretValueReader:
    def __init__(
        self, transaction: Transaction, data_item_repository: DataItemRepository, secret_cipher: SecretCipher
    ) -> None:
        self._transaction = transaction
        self._data_item_repository = data_item_repository
        self._secret_cipher = secret_cipher

    async def list_secret_values(self, project_id: UUID, environment_id: UUID | None) -> list[str]:
        async with self._transaction.begin():
            items = await self._data_item_repository.list_for_environment(project_id, environment_id)
        return [
            self._secret_cipher.decrypt(item.value_encrypted).decode()
            for item in items
            if item.is_secret and item.value_encrypted is not None
        ]

    async def resolve_secrets(
        self, project_id: UUID, environment_id: UUID | None, keys: Collection[str]
    ) -> dict[str, str]:
        async with self._transaction.begin():
            items = await self._data_item_repository.list_for_environment(project_id, environment_id)
        return {
            item.key: self._secret_cipher.decrypt(item.value_encrypted).decode()
            for item in select_effective_items(items, environment_id)
            if item.key in keys and item.is_secret and item.value_encrypted is not None
        }
