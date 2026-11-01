from app.shared.common import Entity


class JiraProject(Entity):
    id: str
    key: str
    name: str
