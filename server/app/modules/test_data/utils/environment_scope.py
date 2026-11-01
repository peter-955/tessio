from uuid import UUID

from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.errors import EnvironmentArchivedError, EnvironmentNotFoundError


async def require_writable_scope(
    environment_repository: EnvironmentRepository, project_id: UUID, environment_id: UUID | None
) -> None:
    if environment_id is None:
        return
    environment = await environment_repository.find_by_id(project_id, environment_id)
    if environment is None:
        raise EnvironmentNotFoundError
    if environment.is_archived:
        raise EnvironmentArchivedError
