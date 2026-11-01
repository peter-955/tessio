from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_data.domains.environment.entity import Environment


class EnvironmentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, project_id: UUID, environment_id: UUID) -> Environment | None: ...

    @abstractmethod
    async def find_by_name(self, project_id: UUID, name: str) -> Environment | None: ...

    @abstractmethod
    async def list(self, project_id: UUID, is_including_archived: bool) -> list[Environment]: ...

    @abstractmethod
    async def save(self, environment: Environment) -> None: ...

    @abstractmethod
    async def delete(self, environment_id: UUID) -> None: ...

    @abstractmethod
    async def clear_project_default(self, environment_id: UUID) -> None: ...
