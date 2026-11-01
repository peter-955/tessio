from uuid import UUID

from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.stories.errors import SprintNotFoundError


async def require_sprint(story_scope_reader: StoryScopeReader, project_id: UUID, sprint_id: UUID) -> SprintReference:
    sprint = await story_scope_reader.find_sprint(project_id, sprint_id)
    if sprint is None:
        raise SprintNotFoundError
    return sprint


async def resolve_sprint(
    story_scope_reader: StoryScopeReader, project_id: UUID, sprint_id: UUID | None
) -> SprintReference | None:
    if sprint_id is not None:
        return await require_sprint(story_scope_reader, project_id, sprint_id)
    return await story_scope_reader.find_current_sprint(project_id)
