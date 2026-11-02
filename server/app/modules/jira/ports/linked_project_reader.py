from abc import ABC, abstractmethod
from uuid import UUID


class LinkedProjectReader(ABC):
    @abstractmethod
    async def list_linked_jira_project_keys(self) -> frozenset[str]: ...

    @abstractmethod
    async def find_project_id_by_jira_project_key(self, jira_project_key: str) -> UUID | None: ...

    @abstractmethod
    async def list_active_jira_project_keys(self) -> list[str]: ...

    @abstractmethod
    async def find_jira_project_key(self, project_id: UUID) -> str | None: ...
