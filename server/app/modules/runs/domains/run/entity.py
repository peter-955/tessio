from datetime import datetime
from uuid import UUID

from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.runs.typing.enums import RunAbortReason, RunExecutor, RunStatus
from app.shared.common import Entity


class Run(Entity):
    id: UUID
    project_id: UUID
    story_id: UUID | None
    environment_id: UUID
    executor: RunExecutor
    status: RunStatus
    abort_reason: RunAbortReason | None
    parent_run_id: UUID | None
    started_by: UUID
    started_via_token_id: UUID | None
    summary: str | None
    report: RunReport | None
    started_at: datetime
    last_activity_at: datetime
    finished_at: datetime | None
    created_at: datetime
    test_suite_id: UUID | None = None
    skipped_cases: list[SkippedRunCase] | None = None

    @property
    def is_running(self) -> bool:
        return self.status is RunStatus.RUNNING
