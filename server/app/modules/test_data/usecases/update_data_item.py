from uuid import UUID

from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.errors import DataItemKeyAlreadyUsedError, DataItemNotFoundError, DataItemValueRequiredError
from app.modules.test_data.typing.enums import DataItemKind
from app.modules.test_data.utils.data_item_capability import require_data_item_edit
from app.modules.test_data.utils.data_item_value import apply_data_item_value
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateDataItemUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        data_item_repository: DataItemRepository,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._data_item_repository = data_item_repository
        self._secret_cipher = secret_cipher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        item_id: UUID,
        item_key: str,
        kind: DataItemKind,
        value: str | None,
    ) -> DataItem:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_DATA_EDIT)
            item = await self._data_item_repository.find_by_id(access.project_id, item_id)
            if item is None:
                raise DataItemNotFoundError
            require_data_item_edit(access, [item.kind, kind])
            if value is None and not (item.is_secret and kind is DataItemKind.SECRET):
                raise DataItemValueRequiredError
            if item_key != item.key:
                same_key_item = await self._data_item_repository.find_by_key(
                    access.project_id, item.environment_id, item_key
                )
                if same_key_item is not None and same_key_item.id != item.id:
                    raise DataItemKeyAlreadyUsedError
            renamed_item = item.model_copy(update={"key": item_key})
            updated_item = (
                renamed_item if value is None else apply_data_item_value(renamed_item, kind, value, self._secret_cipher)
            )
            await self._data_item_repository.save(updated_item)
        return updated_item
