from uuid import UUID

from app.modules.notifications import ReportFormat, ReportSource
from app.shared.common import Entity


class ReportExport(Entity):
    file_id: UUID
    file_name: str
    format: ReportFormat
    source: ReportSource
    source_id: str
    source_label: str
