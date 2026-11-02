from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.domains.saved_data_item.entity import SavedDataItem
from app.modules.test_data.errors import (
    DataKeyIsSecretError,
    EnvironmentArchivedError,
    EnvironmentNotFoundError,
    SecretNotSettableError,
)
from app.modules.test_data.typing.enums import DataItemKind, DataSaveAction, DataToolKind
from app.modules.test_data.utils.data_item_value import apply_data_item_value, build_data_item
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class SetTestDataUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
        data_item_repository: DataItemRepository,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository
        self._data_item_repository = data_item_repository
        self._secret_cipher = secret_cipher

    async def execute_in_token_project(
        self, actor: Actor, item_key: str, value: str, kind: DataToolKind, environment_name: str | None
    ) -> SavedDataItem:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.TEST_DATA_EDIT)
            if kind is DataToolKind.SECRET:
                raise SecretNotSettableError
            environment_id = await self._find_environment_id(access.project_id, environment_name)
            same_key_items = [
                item for item in await self._data_item_repository.list(access.project_id) if item.key == item_key
            ]
            if any(item.is_secret for item in same_key_items):
                raise DataKeyIsSecretError
            existing_item = next((item for item in same_key_items if item.environment_id == environment_id), None)
            if existing_item is None:
                await self._data_item_repository.save(
                    build_data_item(
                        uuid7(),
                        access.project_id,
                        environment_id,
                        item_key,
                        DataItemKind.VARIABLE,
                        value,
                        datetime.now(UTC),
                        self._secret_cipher,
                    )
                )
                action = DataSaveAction.CREATED
            elif existing_item.value == value:
                action = DataSaveAction.UNCHANGED
            else:
                await self._data_item_repository.save(
                    apply_data_item_value(existing_item, DataItemKind.VARIABLE, value, self._secret_cipher)
                )
                action = DataSaveAction.UPDATED
            overridden_in = (
                await self._list_overriding_environment_names(
                    access.project_id, {item.environment_id for item in same_key_items}
                )
                if environment_id is None
                else []
            )
        return SavedDataItem(action=action, overridden_in=overridden_in)

    async def _find_environment_id(self, project_id: UUID, environment_name: str | None) -> UUID | None:
        if environment_name is None:
            return None
        environment = await self._environment_repository.find_by_name(project_id, environment_name.strip())
        if environment is None:
            raise EnvironmentNotFoundError
        if environment.is_archived:
            raise EnvironmentArchivedError
        return environment.id

    async def _list_overriding_environment_names(
        self, project_id: UUID, environment_ids: set[UUID | None]
    ) -> list[str]:
        environments = await self._environment_repository.list(project_id, is_including_archived=False)
        return sorted(environment.name for environment in environments if environment.id in environment_ids)
