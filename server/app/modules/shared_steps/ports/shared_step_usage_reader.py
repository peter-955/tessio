from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.shared_steps.domains.case_step_keys.entity import CaseStepKeys
from app.modules.shared_steps.domains.shared_step_usage.entity import SharedStepUsage


class SharedStepUsageReader(ABC):
    @abstractmethod
    async def count_cases(self, project_id: UUID, keys: Collection[str]) -> dict[str, int]: ...

    @abstractmethod
    async def list_cases(self, project_id: UUID, key: str) -> list[SharedStepUsage]: ...

    @abstractmethod
    async def list_case_step_keys(self, project_id: UUID, key: str) -> list[CaseStepKeys]: ...
