from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.stories.domains.project_sync_state.entity import ProjectSyncState


class ProjectSyncStateRepository(ABC):
    @abstractmethod
    async def find(self, project_id: UUID) -> ProjectSyncState | None: ...

    @abstractmethod
    async def lock(self, project_id: UUID, now: datetime) -> ProjectSyncState: ...

    @abstractmethod
    async def save(self, state: ProjectSyncState) -> None: ...
