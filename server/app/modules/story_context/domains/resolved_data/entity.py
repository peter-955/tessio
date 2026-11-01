from app.shared.common import Entity


class ResolvedData(Entity):
    values: dict[str, str]
    unknown_keys: list[str]
