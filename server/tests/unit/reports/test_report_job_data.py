from uuid import uuid7

from app.modules.notifications import ReportFormat, ReportSource
from app.modules.reports.domains.report_export_job.entity import ReportExportJob
from app.modules.reports.utils.report_job_data import build_report_job_data, parse_report_job_data


def test_job_data_round_trips() -> None:
    job = ReportExportJob(
        file_id=uuid7(),
        project_id=uuid7(),
        project_key="SHOP",
        requester_id=uuid7(),
        source=ReportSource.STORY,
        source_id="SHOP-12",
        format=ReportFormat.PDF,
    )

    assert parse_report_job_data(build_report_job_data(job)) == job


def test_broken_job_data_is_refused() -> None:
    job = ReportExportJob(
        file_id=uuid7(),
        project_id=uuid7(),
        project_key="SHOP",
        requester_id=uuid7(),
        source=ReportSource.RUN,
        source_id=str(uuid7()),
        format=ReportFormat.MARKDOWN,
    )
    data = build_report_job_data(job)

    assert parse_report_job_data({**data, "format": "docx"}) is None
    assert parse_report_job_data({**data, "fileId": "nope"}) is None
    assert parse_report_job_data({key: value for key, value in data.items() if key != "source"}) is None
    assert parse_report_job_data({**data, "projectKey": 7}) is None
