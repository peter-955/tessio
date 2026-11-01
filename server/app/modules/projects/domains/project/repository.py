from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.projects.domains.project.entity import Project


class ProjectRepository(ABC):
    @abstractmethod
    async def find_by_key(self, key: str) -> Project | None: ...

    @abstractmethod
    async def find_by_key_for_update(self, key: str) -> Project | None: ...

    @abstractmethod
    async def find_by_id(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def find_by_jira_project_key(self, jira_project_key: str) -> Project | None: ...

    @abstractmethod
    async def list(self, project_ids: frozenset[UUID] | None, is_including_archived: bool) -> list[Project]: ...

    @abstractmethod
    async def save(self, project: Project) -> None: ...
