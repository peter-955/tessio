from app.shared.common import Entity


class JiraAttachment(Entity):
    file_name: str
    content_type: str
    content: bytes
