from uuid import UUID

from pydantic import JsonValue

from app.modules.notifications import ReportFormat, ReportSource
from app.modules.reports.domains.report_export_job.entity import ReportExportJob
from app.modules.reports.typing.constants import (
    REPORT_JOB_FILE_ID_KEY,
    REPORT_JOB_FORMAT_KEY,
    REPORT_JOB_PROJECT_ID_KEY,
    REPORT_JOB_PROJECT_KEY_KEY,
    REPORT_JOB_REQUESTER_ID_KEY,
    REPORT_JOB_SOURCE_ID_KEY,
    REPORT_JOB_SOURCE_KEY,
)


def build_report_job_data(job: ReportExportJob) -> dict[str, JsonValue]:
    return {
        REPORT_JOB_FILE_ID_KEY: str(job.file_id),
        REPORT_JOB_PROJECT_ID_KEY: str(job.project_id),
        REPORT_JOB_PROJECT_KEY_KEY: job.project_key,
        REPORT_JOB_REQUESTER_ID_KEY: str(job.requester_id),
        REPORT_JOB_SOURCE_KEY: job.source.value,
        REPORT_JOB_SOURCE_ID_KEY: job.source_id,
        REPORT_JOB_FORMAT_KEY: job.format.value,
    }


def parse_report_job_data(data: dict[str, JsonValue]) -> ReportExportJob | None:
    values = {
        key: data.get(key)
        for key in (
            REPORT_JOB_FILE_ID_KEY,
            REPORT_JOB_PROJECT_ID_KEY,
            REPORT_JOB_PROJECT_KEY_KEY,
            REPORT_JOB_REQUESTER_ID_KEY,
            REPORT_JOB_SOURCE_KEY,
            REPORT_JOB_SOURCE_ID_KEY,
            REPORT_JOB_FORMAT_KEY,
        )
    }
    texts = {key: value for key, value in values.items() if isinstance(value, str)}
    if len(texts) != len(values):
        return None
    try:
        return ReportExportJob(
            file_id=UUID(texts[REPORT_JOB_FILE_ID_KEY]),
            project_id=UUID(texts[REPORT_JOB_PROJECT_ID_KEY]),
            project_key=texts[REPORT_JOB_PROJECT_KEY_KEY],
            requester_id=UUID(texts[REPORT_JOB_REQUESTER_ID_KEY]),
            source=ReportSource(texts[REPORT_JOB_SOURCE_KEY]),
            source_id=texts[REPORT_JOB_SOURCE_ID_KEY],
            format=ReportFormat(texts[REPORT_JOB_FORMAT_KEY]),
        )
    except ValueError:
        return None
