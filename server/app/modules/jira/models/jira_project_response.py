from app.shared.common import WireModel


class JiraProjectResponse(WireModel):
    id: str
    key: str
    name: str
