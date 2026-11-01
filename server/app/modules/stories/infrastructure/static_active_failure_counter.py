from uuid import UUID

from app.modules.stories.ports.active_failure_counter import ActiveFailureCounter


class StaticActiveFailureCounter(ActiveFailureCounter):
    def __init__(self, active_count: int = 0) -> None:
        self._active_count = active_count

    async def count_active_for_story(self, project_id: UUID, story_id: UUID) -> int:
        return self._active_count
