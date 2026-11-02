from uuid import UUID

from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.data_key_description.repository import DataKeyDescriptionRepository
from app.modules.test_data.errors import DataItemNotFoundError
from app.modules.test_data.utils.data_item_capability import require_data_item_edit
from app.modules.test_data.utils.data_key_description import remove_unused_key_description
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class DeleteDataItemUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        data_item_repository: DataItemRepository,
        data_key_description_repository: DataKeyDescriptionRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._data_item_repository = data_item_repository
        self._data_key_description_repository = data_key_description_repository

    async def execute(self, actor: Actor, project_key: str, item_id: UUID) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_DATA_EDIT)
            item = await self._data_item_repository.find_by_id(access.project_id, item_id)
            if item is None:
                raise DataItemNotFoundError
            require_data_item_edit(access, [item.kind])
            await self._data_item_repository.delete(item.id)
            await remove_unused_key_description(
                self._data_item_repository, self._data_key_description_repository, access.project_id, item.key
            )
