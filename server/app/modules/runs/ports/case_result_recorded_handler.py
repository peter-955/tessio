from abc import ABC, abstractmethod

from app.modules.runs.domains.recorded_case_result.entity import RecordedCaseResult


class CaseResultRecordedHandler(ABC):
    @abstractmethod
    async def handle(self, recorded: RecordedCaseResult) -> None: ...
