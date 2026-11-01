from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class EnvironmentNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Environment not found.")


class EnvironmentNameAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.ENVIRONMENT_NAME_ALREADY_USED, "An environment with this name already exists.")


class EnvironmentInUseError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.ENVIRONMENT_IN_USE, "Runs use this environment; archive it instead.")


class EnvironmentArchivedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "This environment is archived.")


class DataItemNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Test data item not found.")


class DataItemKeyAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.TEST_DATA_KEY_ALREADY_USED, "This key is already used in this scope.")


class DataItemValueRequiredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Enter a value.")


class DataItemNotSecretError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Only secrets can be revealed.")


class ImportFileNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Import file not found.")


class ImportUploadNotCompletedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UPLOAD_NOT_COMPLETED, "The import file has not been uploaded yet.")


class ImportFileTooLargeError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.FILE_TOO_LARGE, "Import files can be at most 1 MB.")


class ImportInvalidFileError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.IMPORT_INVALID_FILE, "This file cannot be imported.")


class ImportKeyNotInFileError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "A chosen key is not in the import file.")
