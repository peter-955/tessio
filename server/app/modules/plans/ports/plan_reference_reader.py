from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID


class PlanReferenceReader(ABC):
    @abstractmethod
    async def is_active_environment(self, project_id: UUID, environment_id: UUID) -> bool: ...

    @abstractmethod
    async def list_project_suite_ids(self, project_id: UUID, suite_ids: Collection[UUID]) -> set[UUID]: ...

    @abstractmethod
    async def list_project_story_ids(self, project_id: UUID, story_ids: Collection[UUID]) -> set[UUID]: ...
