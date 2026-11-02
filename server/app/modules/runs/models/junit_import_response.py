from uuid import UUID

from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.modules.runs.models.unmapped_test_response import UnmappedTestResponse
from app.modules.runs.typing.enums import RunStatus
from app.shared.common import WireModel


class JunitImportResponse(WireModel):
    run_id: UUID
    status: RunStatus
    counts: RunCountsResponse
    mapped_test_count: int
    unmapped_test_count: int
    unmapped_tests: list[UnmappedTestResponse]
