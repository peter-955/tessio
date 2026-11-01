from uuid import UUID

from app.modules.test_data.ports.environment_usage_checker import EnvironmentUsageChecker


class StaticEnvironmentUsageChecker(EnvironmentUsageChecker):
    def __init__(self, is_used: bool) -> None:
        self._is_used = is_used

    async def is_used_by_runs(self, environment_id: UUID) -> bool:
        return self._is_used
