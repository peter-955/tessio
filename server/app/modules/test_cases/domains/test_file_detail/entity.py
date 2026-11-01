from app.modules.test_cases.domains.test_file.entity import TestFile
from app.modules.test_cases.domains.test_file_version_detail.entity import TestFileVersionDetail
from app.shared.common import Entity


class TestFileDetail(Entity):
    test_file: TestFile
    current_version: TestFileVersionDetail
    version_count: int
