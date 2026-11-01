from app.shared.common import Entity


class EmailMessage(Entity):
    recipient: str
    subject: str
    text: str
