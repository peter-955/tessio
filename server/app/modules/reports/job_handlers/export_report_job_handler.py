from pydantic import JsonValue

from app.modules.reports.usecases.export_report import ExportReportUseCase
from app.modules.reports.utils.report_job_data import parse_report_job_data
from app.shared.common import TessioError
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class ExportReportJobHandler(JobHandler):
    def __init__(self, use_case: ExportReportUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        job = parse_report_job_data(data)
        if job is None:
            log.warning("report.export_invalid_job_data")
            return
        try:
            exported_file = await self._use_case.execute(job)
        except TessioError as error:
            log.warning("report.export_refused", extra={"file_id": str(job.file_id), "code": error.code.value})
            return
        if exported_file is not None:
            log.info("report.exported", extra={"file_id": str(exported_file.id), "size": exported_file.size})
