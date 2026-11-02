from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.runs.domains.blocking_gap.entity import BlockingGap


class RunGapReader(ABC):
    @abstractmethod
    async def list_open_gaps(self, project_id: UUID, story_ids: Collection[UUID]) -> list[BlockingGap]: ...
