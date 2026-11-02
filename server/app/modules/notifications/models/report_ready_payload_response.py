from typing import Literal
from uuid import UUID

from app.modules.notifications.typing.enums import NotificationKind, ReportFormat, ReportSource
from app.shared.common import WireModel


class ReportReadyPayloadResponse(WireModel):
    kind: Literal[NotificationKind.REPORT_READY]
    file_id: UUID
    file_name: str
    format: ReportFormat
    source: ReportSource
    source_id: str
    source_label: str
