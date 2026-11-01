from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListDataItemsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        data_item_repository: DataItemRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._data_item_repository = data_item_repository

    async def execute(self, actor: Actor, project_key: str) -> list[DataItem]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_DATA_VIEW)
            return await self._data_item_repository.list(access.project_id)
