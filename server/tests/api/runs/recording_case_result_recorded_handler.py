from app.modules.runs import CaseResultRecordedHandler, RecordedCaseResult


class RecordingCaseResultRecordedHandler(CaseResultRecordedHandler):
    def __init__(self) -> None:
        self.recorded: list[RecordedCaseResult] = []

    async def handle(self, recorded: RecordedCaseResult) -> None:
        self.recorded.append(recorded)
