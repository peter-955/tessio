from enum import StrEnum


class StoredFileKind(StrEnum):
    SCREENSHOT = "screenshot"
    TEST_FILE = "test_file"
    EVIDENCE = "evidence"
    IMPORT = "import"
    AVATAR = "avatar"
    REPORT = "report"


class StoredFileStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    MISSING = "missing"


class UploadKind(StrEnum):
    TEST_FILE = "test_file"
    EVIDENCE = "evidence"
    IMPORT = "import"
