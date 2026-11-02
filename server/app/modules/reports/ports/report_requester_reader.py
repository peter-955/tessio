from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.reports.domains.report_requester.entity import ReportRequester


class ReportRequesterReader(ABC):
    @abstractmethod
    async def find_requester(self, user_id: UUID) -> ReportRequester | None: ...
