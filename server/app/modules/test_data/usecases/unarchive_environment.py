from uuid import UUID

from app.modules.test_data.domains.environment.entity import Environment
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import EnvironmentNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UnarchiveEnvironmentUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository

    async def execute(self, actor: Actor, project_key: str, environment_id: UUID) -> Environment:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.ENVIRONMENT_MANAGE)
            environment = await self._environment_repository.find_by_id(access.project_id, environment_id)
            if environment is None:
                raise EnvironmentNotFoundError
            unarchived_environment = environment.model_copy(update={"archived_at": None})
            if unarchived_environment != environment:
                await self._environment_repository.save(unarchived_environment)
        return unarchived_environment
