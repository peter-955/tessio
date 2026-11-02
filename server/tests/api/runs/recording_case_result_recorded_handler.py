from app.modules.runs import CaseResultRecordedHandler, RecordedCaseResult
from app.shared.events import LiveEvent


class RecordingCaseResultRecordedHandler(CaseResultRecordedHandler):
    def __init__(self) -> None:
        self.recorded: list[RecordedCaseResult] = []

    async def handle(self, recorded: RecordedCaseResult) -> list[LiveEvent]:
        self.recorded.append(recorded)
        return []
