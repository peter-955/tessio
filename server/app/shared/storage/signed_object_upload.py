from app.shared.common import Entity


class SignedObjectUpload(Entity):
    url: str
    fields: dict[str, str]
