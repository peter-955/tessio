from app.shared.common import WireModel
from app.shared.permissions import Capability, ProjectRole


class AiHarnessMcpToolResponse(WireModel):
    name: str
    description: str
    capability: Capability | None
    roles: list[ProjectRole]
