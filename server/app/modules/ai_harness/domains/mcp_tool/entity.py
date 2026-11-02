from app.shared.common import Entity
from app.shared.permissions import Capability


class McpTool(Entity):
    name: str
    description: str
    capability: Capability | None
