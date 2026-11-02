from fastapi import Request

from app.modules.reports.usecases.request_report_export import RequestReportExportUseCase


def get_request_report_export(request: Request) -> RequestReportExportUseCase:
    use_case: RequestReportExportUseCase = request.app.state.container.request_report_export
    return use_case
