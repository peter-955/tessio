from app.shared.common import WireModel


class ImportResultResponse(WireModel):
    created: int
    updated: int
    unchanged: int
