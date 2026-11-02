from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.insights.domains.failing_case.entity import FailingCase
from app.modules.insights.domains.flaky_case.entity import FlakyCase
from app.modules.insights.domains.label_coverage_report.entity import LabelCoverageReport


class QualityReader(ABC):
    @abstractmethod
    async def get_label_coverage(self, project_id: UUID) -> LabelCoverageReport: ...

    @abstractmethod
    async def list_failing_cases(
        self, project_id: UUID, start_at: datetime, end_at: datetime, limit: int
    ) -> list[FailingCase]: ...

    @abstractmethod
    async def list_flaky_cases(self, project_id: UUID, limit: int) -> list[FlakyCase]: ...
