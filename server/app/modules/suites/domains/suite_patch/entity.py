from app.shared.common import Entity


class SuitePatch(Entity):
    name: str | None
    description: str | None
    is_changing_description: bool
