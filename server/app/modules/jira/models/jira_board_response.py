from app.shared.common import WireModel


class JiraBoardResponse(WireModel):
    id: int
    name: str
    type: str
