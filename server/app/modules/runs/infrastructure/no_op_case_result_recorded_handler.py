from app.modules.runs.domains.recorded_case_result.entity import RecordedCaseResult
from app.modules.runs.ports.case_result_recorded_handler import CaseResultRecordedHandler


class NoOpCaseResultRecordedHandler(CaseResultRecordedHandler):
    async def handle(self, recorded: RecordedCaseResult) -> None:
        return None
