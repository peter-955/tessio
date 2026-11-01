from app.shared.common import Entity


class ImportResult(Entity):
    created: int
    updated: int
    unchanged: int
