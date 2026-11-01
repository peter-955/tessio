from app.shared.common import Entity


class JiraBoard(Entity):
    id: int
    name: str
    type: str
