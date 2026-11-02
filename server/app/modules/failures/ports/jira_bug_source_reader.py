from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.jira_bug_source.entity import JiraBugSource


class JiraBugSourceReader(ABC):
    @abstractmethod
    async def find(self, failure: Failure) -> JiraBugSource | None: ...

    @abstractmethod
    async def find_jira_project_key(self, project_id: UUID) -> str | None: ...
