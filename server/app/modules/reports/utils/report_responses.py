from app.modules.reports.domains.report_export.entity import ReportExport
from app.modules.reports.models.report_export_response import ReportExportResponse


def build_report_export_response(report_export: ReportExport) -> ReportExportResponse:
    return ReportExportResponse(
        file_id=report_export.file_id,
        file_name=report_export.file_name,
        format=report_export.format,
        source=report_export.source,
        source_id=report_export.source_id,
        source_label=report_export.source_label,
    )
