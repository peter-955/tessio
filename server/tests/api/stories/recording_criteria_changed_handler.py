from app.modules.stories import CriteriaChange, CriteriaChangedHandler


class RecordingCriteriaChangedHandler(CriteriaChangedHandler):
    def __init__(self) -> None:
        self.changes: list[CriteriaChange] = []

    async def handle(self, change: CriteriaChange) -> None:
        self.changes.append(change)
