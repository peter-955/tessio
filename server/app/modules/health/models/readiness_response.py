from app.modules.health.typing.enums import DependencyStatus, ReadinessStatus
from app.shared.common import WireModel


class ReadinessResponse(WireModel):
    status: ReadinessStatus
    checks: dict[str, DependencyStatus]
