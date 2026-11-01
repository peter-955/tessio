from datetime import datetime

from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.common import WireModel
from app.shared.typing.enums import ErrorCode


class ProjectSyncStateResponse(WireModel):
    status: ProjectSyncStatus
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    last_succeeded_at: datetime | None
    error_code: ErrorCode | None
