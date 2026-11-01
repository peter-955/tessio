from uuid import UUID

from app.shared.common import Entity


class RunTestFile(Entity):
    test_case_id: UUID
    test_file_version_id: UUID
    key: str
    file_name: str
    object_key: str
    is_uploaded: bool
