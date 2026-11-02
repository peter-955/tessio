from datetime import UTC, datetime
from uuid import uuid7

from app.modules.files import StoredFileKind, StoredFileRepository, build_object_key
from app.modules.files.utils.pending_stored_file import build_pending_stored_file
from app.modules.notifications import ReportFormat, ReportSource
from app.modules.reports.domains.report_export.entity import ReportExport
from app.modules.reports.domains.report_export_job.entity import ReportExportJob
from app.modules.reports.typing.constants import CONTENT_TYPE_BY_FORMAT
from app.modules.reports.usecases.report_document_loader import ReportDocumentLoader
from app.modules.reports.utils.report_file_name import build_report_file_name
from app.modules.reports.utils.report_job_data import build_report_job_data
from app.modules.users import UserLanguage
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName


class RequestReportExportUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        report_document_loader: ReportDocumentLoader,
        stored_file_repository: StoredFileRepository,
        job_queue: JobQueue,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._report_document_loader = report_document_loader
        self._stored_file_repository = stored_file_repository
        self._job_queue = job_queue

    async def execute(
        self, actor: Actor, project_key: str, source: ReportSource, source_id: str, report_format: ReportFormat
    ) -> ReportExport:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            _, label = await self._report_document_loader.load(
                actor, project_key, source, source_id, UserLanguage.EN, now
            )
            file_id = uuid7()
            file_name = build_report_file_name(label.file_stem, report_format)
            await self._stored_file_repository.save(
                build_pending_stored_file(
                    file_id,
                    access.project_id,
                    StoredFileKind.REPORT,
                    build_object_key(access.project_id, StoredFileKind.REPORT, file_id, file_name),
                    file_name,
                    CONTENT_TYPE_BY_FORMAT[report_format],
                    actor.user_id,
                    now,
                )
            )
        job = ReportExportJob(
            file_id=file_id,
            project_id=access.project_id,
            project_key=access.project_key,
            requester_id=actor.user_id,
            source=source,
            source_id=label.source_id,
            format=report_format,
        )
        await self._job_queue.add(
            QueueName.REPORTS, JobName.REPORT_EXPORT, build_report_job_data(job), job_id=str(file_id)
        )
        return ReportExport(
            file_id=file_id,
            file_name=file_name,
            format=report_format,
            source=source,
            source_id=label.source_id,
            source_label=label.label,
        )
