from app.shared.common import Entity


class ImportEntry(Entity):
    key: str
    value: str
    description: str | None = None
