from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.projects.domains.project_member.entity import ProjectMember
from app.shared.permissions import ProjectRole


class ProjectMemberRepository(ABC):
    @abstractmethod
    async def find(self, project_id: UUID, user_id: UUID) -> ProjectMember | None: ...

    @abstractmethod
    async def list_for_user(self, user_id: UUID) -> list[ProjectMember]: ...

    @abstractmethod
    async def count_by_role(self, project_id: UUID, role: ProjectRole) -> int: ...

    @abstractmethod
    async def save(self, project_member: ProjectMember) -> None: ...

    @abstractmethod
    async def delete(self, project_id: UUID, user_id: UUID) -> None: ...
