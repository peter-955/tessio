from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.gaps.domains.gap.entity import Gap
from app.modules.gaps.domains.gap_filter.entity import GapFilter
from app.modules.gaps.domains.gap_view.entity import GapView


class GapRepository(ABC):
    @abstractmethod
    async def find_for_update(self, project_id: UUID, gap_id: UUID) -> Gap | None: ...

    @abstractmethod
    async def add_all(self, gaps: list[Gap]) -> None: ...

    @abstractmethod
    async def save(self, gap: Gap) -> None: ...

    @abstractmethod
    async def count_open(self, story_id: UUID) -> int: ...

    @abstractmethod
    async def find_view(self, project_id: UUID, gap_id: UUID) -> GapView | None: ...

    @abstractmethod
    async def list_views(self, project_id: UUID, gap_filter: GapFilter) -> list[GapView]: ...

    @abstractmethod
    async def list_inbox_views(
        self, user_id: UUID, project_ids: frozenset[UUID], is_including_resolved: bool, limit: int
    ) -> list[GapView]: ...
