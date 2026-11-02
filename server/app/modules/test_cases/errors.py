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


class DraftCasesNotCreatableError(TessioError):
    def __init__(self, indexes: list[int]) -> None:
        self.indexes = indexes
        named_indexes = ", ".join(str(index) for index in indexes)
        super().__init__(
            ErrorCode.INVALID_REQUEST,
            f"Cases {named_indexes} have a problem. Nothing was created; "
            "send only cases that check_draft_cases accepts.",
        )


class TestCaseVersionNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Test case version not found.")


class ReviewCommentNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Review comment not found.")


class ReviewCommentStepNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Comment on a step of this version.")


class ReviewCommentOnDeprecatedCaseError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "Restore the test case to Draft before commenting on it.")


class ReviewCommentsOpenError(TessioError):
    def __init__(self, open_count: int) -> None:
        self.open_count = open_count
        super().__init__(
            ErrorCode.REVIEW_COMMENTS_OPEN,
            f"Resolve the open review comments ({open_count}) before marking the case Ready.",
        )


class ReviewerIsAuthorError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.REVIEWER_IS_AUTHOR,
            "This project needs a reviewer who did not write the version under review.",
        )


class SecretInDataRowError(TessioError):
    def __init__(self, row_number: int) -> None:
        self.row_number = row_number
        super().__init__(
            ErrorCode.SECRET_IN_DATA_ROW,
            f"Data row {row_number} holds a secret value. Use a {{{{data.key}}}} reference to a secret key instead.",
        )
