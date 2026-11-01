from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class TestCaseNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Test case not found.")


class StoryNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Story not found.")


class TestFileNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Test file not found.")


class TestCaseVersionConflictError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "Someone saved a newer version. Reload and try again.")


class TestCaseDeprecatedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "Restore the test case to Draft before editing it.")


class InvalidTestCaseStatusTransitionError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_STATUS_TRANSITION, "This test case status change is not allowed.")


class CaseNotReadyError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CASE_NOT_READY, "Add at least one step before marking the case Ready.")


class UnknownReferenceError(TessioError):
    def __init__(self, references: list[str]) -> None:
        self.references = references
        named_references = ", ".join(f"{{{{{reference}}}}}" for reference in references)
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, f"Unknown references: {named_references}.")


class CriterionNotLinkableError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Link only current acceptance criteria of this story.")


class StoredFileNotUsableError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Upload the file as a test file.")


class StoredFileAlreadyAttachedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "This file is already attached to a test case.")


class UploadNotCompletedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UPLOAD_NOT_COMPLETED, "The file has not been uploaded yet.")


class CaseImportFileNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Import file not found.")


class CaseImportUploadNotCompletedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UPLOAD_NOT_COMPLETED, "The import file has not been uploaded yet.")


class CaseImportFileTooLargeError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.FILE_TOO_LARGE, "Import files can be at most 5 MB.")


class ImportInvalidFileError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.IMPORT_INVALID_FILE, "This file cannot be imported.")


class CaseImportChoiceInvalidError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "A chosen case cannot be imported.")
