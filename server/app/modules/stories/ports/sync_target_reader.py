from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.stories.domains.sync_target.entity import SyncTarget


class SyncTargetReader(ABC):
    @abstractmethod
    async def find(self, project_id: UUID) -> SyncTarget | None: ...
