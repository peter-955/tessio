from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.notifications import ReportSource
from app.modules.projects import get_signed_in_actor
from app.modules.reports.dependencies import get_request_report_export
from app.modules.reports.models.export_report_request import ExportReportRequest
from app.modules.reports.models.report_export_response import ReportExportResponse
from app.modules.reports.usecases.request_report_export import RequestReportExportUseCase
from app.modules.reports.utils.report_responses import build_report_export_response
from app.shared.permissions import Actor

reports_router = APIRouter(prefix="/api", tags=["reports"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]
RequestReportExport = Annotated[RequestReportExportUseCase, Depends(get_request_report_export)]


@reports_router.post("/projects/{project_key}/runs/{run_id}/export", status_code=status.HTTP_202_ACCEPTED)
async def export_run_report(
    project_key: str, run_id: UUID, body: ExportReportRequest, actor: SignedInActor, use_case: RequestReportExport
) -> ReportExportResponse:
    report_export = await use_case.execute(actor, project_key, ReportSource.RUN, str(run_id), body.format)
    return build_report_export_response(report_export)


@reports_router.post("/projects/{project_key}/plans/{plan_id}/export", status_code=status.HTTP_202_ACCEPTED)
async def export_plan_report(
    project_key: str, plan_id: UUID, body: ExportReportRequest, actor: SignedInActor, use_case: RequestReportExport
) -> ReportExportResponse:
    report_export = await use_case.execute(actor, project_key, ReportSource.PLAN, str(plan_id), body.format)
    return build_report_export_response(report_export)


@reports_router.post("/projects/{project_key}/stories/{jira_key}/export", status_code=status.HTTP_202_ACCEPTED)
async def export_story_report(
    project_key: str, jira_key: str, body: ExportReportRequest, actor: SignedInActor, use_case: RequestReportExport
) -> ReportExportResponse:
    report_export = await use_case.execute(actor, project_key, ReportSource.STORY, jira_key, body.format)
    return build_report_export_response(report_export)
