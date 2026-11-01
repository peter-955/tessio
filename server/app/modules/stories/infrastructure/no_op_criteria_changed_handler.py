from app.modules.stories.domains.criteria_change.entity import CriteriaChange
from app.modules.stories.ports.criteria_changed_handler import CriteriaChangedHandler


class NoOpCriteriaChangedHandler(CriteriaChangedHandler):
    async def handle(self, change: CriteriaChange) -> None:
        return None
