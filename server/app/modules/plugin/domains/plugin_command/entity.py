from app.shared.common import Entity


class PluginCommand(Entity):
    name: str
    description: str
    argument_hint: str | None
