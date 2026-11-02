from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID


class JiraResultCommentRequester(ABC):
    @abstractmethod
    async def request_after_sign_off(self, project_id: UUID, story_id: UUID) -> None: ...

    @abstractmethod
    async def request_after_run(self, project_id: UUID, run_id: UUID, story_ids: Collection[UUID]) -> None: ...
