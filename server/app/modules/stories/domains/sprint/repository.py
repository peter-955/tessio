from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.stories.domains.sprint.entity import Sprint
from app.modules.stories.domains.sprint_overview.entity import SprintOverview


class SprintRepository(ABC):
    @abstractmethod
    async def find_overview(self, project_id: UUID, sprint_id: UUID) -> SprintOverview | None: ...

    @abstractmethod
    async def find_by_id(self, project_id: UUID, sprint_id: UUID) -> Sprint | None: ...

    @abstractmethod
    async def list_by_project(self, project_id: UUID) -> list[Sprint]: ...

    @abstractmethod
    async def save_synced(self, sprint: Sprint) -> UUID: ...

    @abstractmethod
    async def list(self, project_id: UUID) -> list[SprintOverview]: ...
