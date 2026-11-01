from abc import ABC, abstractmethod
from uuid import UUID

from app.shared.permissions import ProjectRole


class RecipientDirectory(ABC):
    @abstractmethod
    async def list_active_recipient_ids(
        self, project_id: UUID, user_ids: frozenset[UUID], roles: frozenset[ProjectRole]
    ) -> frozenset[UUID]: ...
