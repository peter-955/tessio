from uuid import UUID

from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import EnvironmentNotFoundError
from app.modules.test_data.utils.effective_data_items import select_effective_items
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListEffectiveDataItemsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
        data_item_repository: DataItemRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository
        self._data_item_repository = data_item_repository

    async def execute(self, actor: Actor, project_key: str, environment_id: UUID | None) -> list[DataItem]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_DATA_VIEW)
            if (
                environment_id is not None
                and await self._environment_repository.find_by_id(access.project_id, environment_id) is None
            ):
                raise EnvironmentNotFoundError
            items = await self._data_item_repository.list_for_environment(access.project_id, environment_id)
        return select_effective_items(items, environment_id)
