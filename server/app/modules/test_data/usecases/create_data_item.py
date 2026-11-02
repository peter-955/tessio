from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.data_key_description.repository import DataKeyDescriptionRepository
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import DataItemKeyAlreadyUsedError
from app.modules.test_data.typing.enums import DataItemKind
from app.modules.test_data.utils.data_item_capability import require_data_item_edit
from app.modules.test_data.utils.data_item_value import build_data_item
from app.modules.test_data.utils.data_key_description import apply_key_description
from app.modules.test_data.utils.environment_scope import require_writable_scope
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, ProjectAccessResolver


class CreateDataItemUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
        data_item_repository: DataItemRepository,
        data_key_description_repository: DataKeyDescriptionRepository,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository
        self._data_item_repository = data_item_repository
        self._data_key_description_repository = data_key_description_repository
        self._secret_cipher = secret_cipher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        item_key: str,
        kind: DataItemKind,
        value: str,
        environment_id: UUID | None,
        description: str | None,
    ) -> DataItem:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require_data_item_edit(access, [kind])
            await require_writable_scope(self._environment_repository, access.project_id, environment_id)
            if await self._data_item_repository.find_by_key(access.project_id, environment_id, item_key) is not None:
                raise DataItemKeyAlreadyUsedError
            item = build_data_item(
                uuid7(),
                access.project_id,
                environment_id,
                item_key,
                kind,
                value,
                datetime.now(UTC),
                self._secret_cipher,
            )
            await self._data_item_repository.save(item)
            key_description = await apply_key_description(
                self._data_key_description_repository, access.project_id, item_key, description
            )
        return item.model_copy(update={"description": key_description})
