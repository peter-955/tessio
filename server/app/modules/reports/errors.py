from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class ReportSourceNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Nothing to export was found.")
