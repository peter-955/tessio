from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class LabelNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Label not found.")


class LabelNameAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "A label with this name already exists.")


class LabelNotInProjectError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Use only labels of this project.")
