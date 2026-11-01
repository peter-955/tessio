from uuid import UUID

from app.modules.stories.ports.running_run_checker import RunningRunChecker


class StaticRunningRunChecker(RunningRunChecker):
    def __init__(self, is_running: bool = False) -> None:
        self._is_running = is_running

    async def has_running_run(self, project_id: UUID, story_id: UUID) -> bool:
        return self._is_running
