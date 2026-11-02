from uuid import UUID

from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.modules.shared_steps.domains.shared_step.repository import SharedStepRepository
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion
from app.modules.shared_steps.errors import SharedStepNotFoundError


def normalize_shared_step_key(key: str) -> str:
    return key.strip().lower()


async def require_shared_step(repository: SharedStepRepository, project_id: UUID, key: str) -> SharedStep:
    shared_step = await repository.find_by_key(project_id, normalize_shared_step_key(key))
    if shared_step is None:
        raise SharedStepNotFoundError
    return shared_step


async def require_locked_shared_step(repository: SharedStepRepository, project_id: UUID, key: str) -> SharedStep:
    shared_step = await repository.find_by_key_for_update(project_id, normalize_shared_step_key(key))
    if shared_step is None:
        raise SharedStepNotFoundError
    return shared_step


async def require_current_shared_step_version(
    repository: SharedStepRepository, shared_step: SharedStep
) -> SharedStepVersion:
    version = await repository.find_version(shared_step.current_version_id)
    if version is None:
        raise SharedStepNotFoundError
    return version
