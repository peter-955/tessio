from app.modules.health.typing.enums import LivenessStatus
from app.shared.common import WireModel


class HealthResponse(WireModel):
    status: LivenessStatus
