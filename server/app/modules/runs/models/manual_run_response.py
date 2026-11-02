from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.modules.runs.models.manual_run_case_response import ManualRunCaseResponse
from app.modules.runs.models.skipped_run_case_response import SkippedRunCaseResponse
from app.modules.runs.typing.enums import RunAbortReason, RunExecutor, RunStatus
from app.shared.common import WireModel


class ManualRunResponse(WireModel):
    id: UUID
    story_id: UUID | None
    environment_id: UUID
    executor: RunExecutor
    status: RunStatus
    parent_run_id: UUID | None
    started_by: UUID
    started_at: datetime
    finished_at: datetime | None
    abort_reason: RunAbortReason | None
    summary: str | None
    cases: list[ManualRunCaseResponse]
    test_suite_id: UUID | None = None
    skipped_cases: list[SkippedRunCaseResponse] = Field(default_factory=list)
