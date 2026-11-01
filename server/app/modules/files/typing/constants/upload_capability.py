from app.modules.files.typing.enums import StoredFileKind, UploadKind
from app.shared.permissions import Capability

UPLOAD_CAPABILITY_BY_KIND = {
    UploadKind.TEST_FILE: Capability.TEST_CASE_EDIT,
    UploadKind.EVIDENCE: Capability.RUN_RECORD_MANUAL,
    UploadKind.IMPORT: Capability.TEST_DATA_EDIT,
}
UPLOAD_KIND_BY_FILE_KIND = {
    StoredFileKind.TEST_FILE: UploadKind.TEST_FILE,
    StoredFileKind.EVIDENCE: UploadKind.EVIDENCE,
    StoredFileKind.IMPORT: UploadKind.IMPORT,
}
