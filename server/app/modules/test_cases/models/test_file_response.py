from uuid import UUID

from app.modules.test_cases.models.test_file_version_response import TestFileVersionResponse
from app.shared.common import WireModel


class TestFileResponse(WireModel):
    id: UUID
    key: str
    current_version: TestFileVersionResponse
    version_count: int
