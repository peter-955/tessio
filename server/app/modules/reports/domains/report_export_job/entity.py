from uuid import UUID

from app.modules.notifications import ReportFormat, ReportSource
from app.shared.common import Entity


class ReportExportJob(Entity):
    file_id: UUID
    project_id: UUID
    project_key: str
    requester_id: UUID
    source: ReportSource
    source_id: str
    format: ReportFormat
