from app.modules.health.typing.enums import DependencyStatus
from app.shared.common import Entity


class ReadinessReport(Entity):
    checks: dict[str, DependencyStatus]

    @property
    def is_ready(self) -> bool:
        return all(status is DependencyStatus.OK for status in self.checks.values())
