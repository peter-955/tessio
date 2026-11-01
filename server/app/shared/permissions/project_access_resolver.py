from abc import ABC, abstractmethod
from uuid import UUID

from app.shared.permissions.actor import Actor
from app.shared.permissions.project_access import ProjectAccess


class ProjectAccessResolver(ABC):
    @abstractmethod
    async def resolve(self, actor: Actor, project_key: str) -> ProjectAccess: ...

    @abstractmethod
    async def resolve_by_id(self, actor: Actor, project_id: UUID) -> ProjectAccess: ...

    @abstractmethod
    async def list_visible_project_ids(self, actor: Actor) -> frozenset[UUID]: ...
