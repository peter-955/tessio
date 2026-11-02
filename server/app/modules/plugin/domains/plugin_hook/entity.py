from app.shared.common import Entity


class PluginHook(Entity):
    event: str
    matcher: str | None
    command: str
    timeout_seconds: int | None
