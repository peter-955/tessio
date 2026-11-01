from uuid import UUID

from app.modules.test_data.domains.environment.entity import Environment
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import EnvironmentNameAlreadyUsedError, EnvironmentNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateEnvironmentUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        environment_id: UUID,
        name: str,
        base_url: str,
        health_check_url: str | None,
    ) -> Environment:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.ENVIRONMENT_MANAGE)
            environment = await self._environment_repository.find_by_id(access.project_id, environment_id)
            if environment is None:
                raise EnvironmentNotFoundError
            same_name_environment = await self._environment_repository.find_by_name(access.project_id, name)
            if same_name_environment is not None and same_name_environment.id != environment.id:
                raise EnvironmentNameAlreadyUsedError
            updated_environment = environment.model_copy(
                update={"name": name, "base_url": base_url, "health_check_url": health_check_url}
            )
            if updated_environment != environment:
                await self._environment_repository.save(updated_environment)
        return updated_environment
