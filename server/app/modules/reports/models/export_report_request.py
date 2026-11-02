from app.modules.notifications import ReportFormat
from app.shared.common import WireModel


class ExportReportRequest(WireModel):
    format: ReportFormat
