from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.shared_steps.domains.current_shared_step.entity import CurrentSharedStep
from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion


class SharedStepRepository(ABC):
    @abstractmethod
    async def find_by_key(self, project_id: UUID, key: str) -> SharedStep | None: ...

    @abstractmethod
    async def find_by_key_for_update(self, project_id: UUID, key: str) -> SharedStep | None: ...

    @abstractmethod
    async def find_version(self, version_id: UUID) -> SharedStepVersion | None: ...

    @abstractmethod
    async def list_current(self, project_id: UUID, is_including_archived: bool) -> list[CurrentSharedStep]: ...

    @abstractmethod
    async def list_current_by_keys(self, project_id: UUID, keys: Collection[str]) -> list[CurrentSharedStep]: ...

    @abstractmethod
    async def add(self, shared_step: SharedStep, version: SharedStepVersion) -> None: ...

    @abstractmethod
    async def add_version(self, shared_step: SharedStep, version: SharedStepVersion) -> None: ...

    @abstractmethod
    async def save(self, shared_step: SharedStep) -> None: ...
