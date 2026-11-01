from app.modules.test_cases.domains.test_file_version.entity import TestFileVersion
from app.shared.common import Entity


class TestFileVersionDetail(Entity):
    version: TestFileVersion
    file_name: str
    content_type: str
    size: int | None
