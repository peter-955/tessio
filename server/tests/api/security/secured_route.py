from app.shared.common import Entity
from app.shared.permissions import Capability, WorkspaceCapability
from tests.api.security.route_access import RouteAccess


class SecuredRoute(Entity):
    method: str
    path: str
    access: RouteAccess
    capability: Capability | WorkspaceCapability | None
    body: dict[str, object] | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.method, self.path)
