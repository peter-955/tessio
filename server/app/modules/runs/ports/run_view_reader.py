from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.files import StoredFileStatus
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_file.entity import RunCaseFile
from app.modules.runs.domains.run_criterion.entity import RunCriterion
from app.modules.runs.domains.run_filter.entity import RunFilter
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.modules.runs.domains.run_summary.entity import RunSummary


class RunViewReader(ABC):
    @abstractmethod
    async def list_summaries(self, project_id: UUID, run_filter: RunFilter) -> list[RunSummary]: ...

    @abstractmethod
    async def find_labels(self, run: Run) -> RunLabels: ...

    @abstractmethod
    async def list_screenshot_statuses(self, run_id: UUID) -> dict[UUID, StoredFileStatus]: ...

    @abstractmethod
    async def list_child_run_ids(self, run_id: UUID) -> list[UUID]: ...

    @abstractmethod
    async def map_active_criteria(self, criterion_ids: Collection[UUID]) -> dict[UUID, RunCriterion]: ...

    @abstractmethod
    async def map_case_files(self, file_version_ids: Collection[UUID]) -> dict[UUID, RunCaseFile]: ...
