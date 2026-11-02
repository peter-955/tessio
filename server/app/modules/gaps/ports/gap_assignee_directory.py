from abc import ABC, abstractmethod
from collections.abc import Mapping
from uuid import UUID

from app.modules.gaps.domains.gap_assignee.entity import GapAssignee
from app.shared.permissions import ProjectRole


class GapAssigneeDirectory(ABC):
    @abstractmethod
    async def list_active_member_ids(
        self, project_id: UUID, roles: frozenset[ProjectRole]
    ) -> Mapping[ProjectRole, list[UUID]]: ...

    @abstractmethod
    async def find_active_member_role(self, project_id: UUID, user_id: UUID) -> ProjectRole | None: ...

    @abstractmethod
    async def list_assignable_members(self, project_id: UUID) -> list[GapAssignee]: ...
