from datetime import datetime
from uuid import UUID

from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.common import Entity
from app.shared.typing.enums import ErrorCode


class ProjectSyncState(Entity):
    project_id: UUID
    status: ProjectSyncStatus
    requested_by: UUID | None
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    last_succeeded_at: datetime | None
    error_code: ErrorCode | None

    @property
    def is_in_progress(self) -> bool:
        return self.status in {ProjectSyncStatus.QUEUED, ProjectSyncStatus.RUNNING}
