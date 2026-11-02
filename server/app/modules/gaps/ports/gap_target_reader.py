from abc import ABC, abstractmethod
from collections.abc import Mapping
from uuid import UUID

from app.modules.gaps.domains.gap_case.entity import GapCase
from app.modules.gaps.domains.gap_story.entity import GapStory


class GapTargetReader(ABC):
    @abstractmethod
    async def find_story(self, project_id: UUID, jira_key: str) -> GapStory | None: ...

    @abstractmethod
    async def find_criterion_id(self, story_id: UUID, code: str) -> UUID | None: ...

    @abstractmethod
    async def find_test_case_id(self, story_id: UUID, code: str) -> UUID | None: ...

    @abstractmethod
    async def list_criterion_texts(self, criterion_ids: frozenset[UUID]) -> Mapping[UUID, str]: ...

    @abstractmethod
    async def list_cases(self, test_case_ids: frozenset[UUID]) -> Mapping[UUID, GapCase]: ...
