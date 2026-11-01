from app.modules.files.typing.enums import StoredFileKind

DOWNLOADABLE_FILE_KINDS = frozenset(
    {StoredFileKind.SCREENSHOT, StoredFileKind.TEST_FILE, StoredFileKind.EVIDENCE, StoredFileKind.REPORT}
)
