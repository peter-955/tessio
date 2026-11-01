from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class FileTypeNotAllowedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.FILE_TYPE_NOT_ALLOWED, "This file type is not allowed.")


class FileTooLargeError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.FILE_TOO_LARGE, "This file is too large.")


class UploadNotCompletedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UPLOAD_NOT_COMPLETED, "The file has not been uploaded yet.")


class StoredFileNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "File not found.")


class UnsupportedUploadKindError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "This kind of file cannot be uploaded here.")
