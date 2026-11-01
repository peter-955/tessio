from datetime import UTC, datetime
from uuid import uuid7

from app.modules.test_data.domains.environment.entity import Environment
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import EnvironmentNameAlreadyUsedError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateEnvironmentUseCase:
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
        self, actor: Actor, project_key: str, name: str, base_url: str, health_check_url: str | None
    ) -> Environment:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.ENVIRONMENT_MANAGE)
            if await self._environment_repository.find_by_name(access.project_id, name) is not None:
                raise EnvironmentNameAlreadyUsedError
            environment = Environment(
                id=uuid7(),
                project_id=access.project_id,
                name=name,
                base_url=base_url,
                health_check_url=health_check_url,
                archived_at=None,
                created_at=datetime.now(UTC),
            )
            await self._environment_repository.save(environment)
        return environment
