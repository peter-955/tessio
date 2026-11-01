from app.shared.common import WireModel
from app.shared.typing.enums import ErrorCode


class ErrorResponse(WireModel):
    code: ErrorCode
    message: str
