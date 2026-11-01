from datetime import datetime
from uuid import UUID

from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.modules.runs.typing.enums import RunAbortReason, RunExecutor, RunStatus
from app.shared.common import WireModel


class RunSummaryResponse(WireModel):
    id: UUID
    story_id: UUID
    story_jira_key: str
    story_title: str
    environment_id: UUID
    environment_name: str
    executor: RunExecutor
    status: RunStatus
    abort_reason: RunAbortReason | None
    parent_run_id: UUID | None
    started_by: UUID
    started_by_name: str
    started_at: datetime
    finished_at: datetime | None
    counts: RunCountsResponse
