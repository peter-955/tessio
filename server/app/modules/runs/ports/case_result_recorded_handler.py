from abc import ABC, abstractmethod

from app.modules.runs.domains.recorded_case_result.entity import RecordedCaseResult
from app.shared.events import LiveEvent


class CaseResultRecordedHandler(ABC):
    @abstractmethod
    async def handle(self, recorded: RecordedCaseResult) -> list[LiveEvent]: ...
