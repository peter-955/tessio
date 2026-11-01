from app.shared.common import Entity


class SignedUpload(Entity):
    url: str
    fields: dict[str, str]
    key_prefix: str
