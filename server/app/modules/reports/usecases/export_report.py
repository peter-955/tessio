import hashlib
from datetime import UTC, datetime

from app.modules.files import StoredFile, StoredFileRepository, StoredFileStatus
from app.modules.notifications import ReportFormat, ReportReadyPayload, SendNotificationUseCase
from app.modules.reports.domains.report_export_job.entity import ReportExportJob
from app.modules.reports.ports.pdf_renderer import PdfRenderer
from app.modules.reports.ports.report_file_writer import ReportFileWriter
from app.modules.reports.ports.report_requester_reader import ReportRequesterReader
from app.modules.reports.usecases.report_document_loader import ReportDocumentLoader
from app.modules.reports.utils.html_report import render_html
from app.modules.reports.utils.markdown_report import render_markdown
from app.modules.reports.utils.report_masking import mask_document
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.logging import get_logger
from app.shared.masking import SecretMasker
from app.shared.permissions import Actor

log = get_logger(__name__)


class ExportReportUseCase:
    def __init__(
        self,
        transaction: Transaction,
        stored_file_repository: StoredFileRepository,
        report_requester_reader: ReportRequesterReader,
        report_document_loader: ReportDocumentLoader,
        secret_value_reader: SecretValueReader,
        pdf_renderer: PdfRenderer,
        report_file_writer: ReportFileWriter,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._stored_file_repository = stored_file_repository
        self._report_requester_reader = report_requester_reader
        self._report_document_loader = report_document_loader
        self._secret_value_reader = secret_value_reader
        self._pdf_renderer = pdf_renderer
        self._report_file_writer = report_file_writer
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher

    async def execute(self, job: ReportExportJob) -> StoredFile | None:
        async with self._transaction.begin():
            stored_file = await self._stored_file_repository.find_by_id(job.file_id)
            requester = await self._report_requester_reader.find_requester(job.requester_id)
        if stored_file is None or stored_file.project_id != job.project_id or not stored_file.is_pending:
            log.warning("report.export_file_missing", extra={"file_id": str(job.file_id)})
            return None
        if requester is None or not requester.is_active:
            log.warning("report.export_requester_inactive", extra={"file_id": str(job.file_id)})
            return None
        actor = Actor(user_id=requester.user_id, workspace_role=requester.workspace_role)
        document, label = await self._report_document_loader.load(
            actor, job.project_key, job.source, job.source_id, requester.language, datetime.now(UTC)
        )
        masker = SecretMasker(await self._secret_value_reader.list_project_secret_values(job.project_id))
        masked_document = mask_document(document, masker)
        content = (
            render_markdown(masked_document).encode()
            if job.format is ReportFormat.MARKDOWN
            else await self._pdf_renderer.render(render_html(masked_document, requester.language))
        )
        await self._report_file_writer.write(stored_file.object_key, content, stored_file.content_type)
        uploaded_file = stored_file.model_copy(
            update={
                "status": StoredFileStatus.UPLOADED,
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
        async with self._transaction.begin():
            await self._stored_file_repository.save(uploaded_file)
        await self._send_notification.execute(
            job.project_id,
            ReportReadyPayload(
                file_id=uploaded_file.id,
                file_name=uploaded_file.file_name,
                format=job.format,
                source=job.source,
                source_id=label.source_id,
                source_label=masker.mask(label.label),
            ),
            None,
            recipient_ids=[requester.user_id],
        )
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.REPORT_READY,
                project_id=job.project_id,
                user_id=requester.user_id,
                ids={"fileId": str(uploaded_file.id), "format": job.format.value},
            )
        )
        return uploaded_file
