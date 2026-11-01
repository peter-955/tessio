from app.modules.test_data.domains.environment.entity import Environment
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListEnvironmentsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository

    async def execute(self, actor: Actor, project_key: str, is_including_archived: bool) -> list[Environment]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.PROJECT_VIEW)
            return await self._environment_repository.list(access.project_id, is_including_archived)
