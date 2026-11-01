from uuid import UUID

from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import EnvironmentInUseError, EnvironmentNotFoundError
from app.modules.test_data.ports.environment_usage_checker import EnvironmentUsageChecker
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class DeleteEnvironmentUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
        environment_usage_checker: EnvironmentUsageChecker,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository
        self._environment_usage_checker = environment_usage_checker

    async def execute(self, actor: Actor, project_key: str, environment_id: UUID) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.ENVIRONMENT_MANAGE)
            environment = await self._environment_repository.find_by_id(access.project_id, environment_id)
            if environment is None:
                raise EnvironmentNotFoundError
            if await self._environment_usage_checker.is_used_by_runs(environment.id):
                raise EnvironmentInUseError
            await self._environment_repository.delete(environment.id)
