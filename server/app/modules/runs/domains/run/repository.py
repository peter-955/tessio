from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.runs.domains.run.entity import Run


class RunRepository(ABC):
    @abstractmethod
    async def find_by_id(self, project_id: UUID, run_id: UUID) -> Run | None: ...

    @abstractmethod
    async def find_by_id_for_update(self, project_id: UUID, run_id: UUID) -> Run | None: ...

    @abstractmethod
    async def has_running_for_story(self, project_id: UUID, story_id: UUID) -> bool: ...

    @abstractmethod
    async def is_environment_used(self, environment_id: UUID) -> bool: ...

    @abstractmethod
    async def list_stale_run_ids(self, cutoff: datetime, limit: int) -> list[UUID]: ...

    @abstractmethod
    async def find_stale_for_update(self, run_id: UUID, cutoff: datetime) -> Run | None: ...

    @abstractmethod
    async def add(self, run: Run) -> None: ...

    @abstractmethod
    async def save(self, run: Run) -> None: ...
