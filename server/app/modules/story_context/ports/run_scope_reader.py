from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.story_context.domains.run_scope.entity import RunScope
from app.modules.story_context.domains.run_test_file.entity import RunTestFile


class RunScopeReader(ABC):
    @abstractmethod
    async def find_run(self, project_id: UUID, run_id: UUID) -> RunScope | None: ...

    @abstractmethod
    async def list_data_keys(self, run_id: UUID) -> frozenset[str]: ...

    @abstractmethod
    async def list_test_files(self, run_id: UUID, key: str, test_case_id: UUID | None) -> list[RunTestFile]: ...
