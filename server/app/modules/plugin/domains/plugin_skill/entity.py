from app.shared.common import Entity


class PluginSkill(Entity):
    name: str
    description: str
    argument_hint: str | None
