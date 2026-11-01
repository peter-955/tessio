from uuid import UUID

from app.shared.permissions import Actor, ProjectAccess, ProjectAccessResolver


class StaticProjectAccessResolver(ProjectAccessResolver):
    def __init__(self) -> None:
        self.project_ids_by_user_id: dict[UUID, set[UUID]] = {}

    async def resolve(self, actor: Actor, project_key: str) -> ProjectAccess:
        raise NotImplementedError

    async def resolve_by_id(self, actor: Actor, project_id: UUID) -> ProjectAccess:
        raise NotImplementedError

    async def list_visible_project_ids(self, actor: Actor) -> frozenset[UUID]:
        return frozenset(self.project_ids_by_user_id.get(actor.user_id, set()))
