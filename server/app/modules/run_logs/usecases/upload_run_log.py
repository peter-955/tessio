from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.run_logs.domains.run_log.entity import RunLog
from app.modules.run_logs.domains.run_log.repository import RunLogRepository
from app.modules.run_logs.domains.run_log_entry.entity import RunLogEntry
from app.modules.run_logs.domains.uploaded_run_log.entity import UploadedRunLog
from app.modules.run_logs.errors import (
    RunLogManualRunError,
    RunLogNotOwnedError,
    RunLogTooEarlyError,
    RunLogTooLateError,
    RunNotFoundError,
)
from app.modules.run_logs.typing.constants import RUN_LOG_UPLOAD_WINDOW
from app.modules.run_logs.typing.enums import RunLogEntryKind
from app.modules.run_logs.utils.run_log_masking import clean_input, clean_text
from app.modules.run_logs.utils.run_log_phases import assign_phases
from app.modules.runs import RunCaseRepository, RunExecutor, RunRepository
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.masking import SecretMasker
from app.shared.permissions import Actor, ProjectNotFoundError


class UploadRunLogUseCase:
    def __init__(
        self,
        transaction: Transaction,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        run_log_repository: RunLogRepository,
        secret_value_reader: SecretValueReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._run_log_repository = run_log_repository
        self._secret_value_reader = secret_value_reader
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, run_id: UUID, uploaded_log: UploadedRunLog) -> RunLog:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            run = await self._run_repository.find_by_id(actor.token_project_id, run_id)
            if run is None:
                raise RunNotFoundError
            if run.started_by != actor.user_id:
                raise RunLogNotOwnedError
            if run.executor is not RunExecutor.CLAUDE:
                raise RunLogManualRunError
            if run.finished_at is None:
                raise RunLogTooEarlyError
            if now - run.finished_at > RUN_LOG_UPLOAD_WINDOW:
                raise RunLogTooLateError
            case_ids = {run_case.test_case_id for run_case in await self._run_case_repository.list_for_run(run.id)}
            masker = SecretMasker(
                await self._secret_value_reader.list_secret_values(run.project_id, run.environment_id)
            )
            placed_entries = zip(uploaded_log.entries, assign_phases(uploaded_log.entries, case_ids), strict=True)
            entries = [
                RunLogEntry(
                    id=uuid7(),
                    run_id=run.id,
                    position=position,
                    phase=phase,
                    test_case_id=test_case_id,
                    kind=entry.kind,
                    at=entry.at,
                    tool=entry.tool if entry.kind is RunLogEntryKind.ACTION else None,
                    input=clean_input(entry.input, masker) if entry.kind is RunLogEntryKind.ACTION else None,
                    output=clean_text(entry.text if entry.kind is RunLogEntryKind.NOTE else entry.output, masker),
                    is_error=entry.is_error,
                    duration_ms=entry.duration_ms,
                )
                for position, (entry, (phase, test_case_id)) in enumerate(placed_entries)
            ]
            run_log = RunLog(
                run_id=run.id,
                received_at=now,
                is_cut=uploaded_log.is_cut,
                input_tokens=uploaded_log.input_tokens,
                cache_creation_input_tokens=uploaded_log.cache_creation_input_tokens,
                cache_read_input_tokens=uploaded_log.cache_read_input_tokens,
                output_tokens=uploaded_log.output_tokens,
            )
            await self._run_log_repository.replace(run_log, entries)
        await self._live_event_publisher.publish(
            LiveEvent(type=LiveEventType.RUN_LOG_RECEIVED, project_id=run.project_id, ids={"runId": str(run.id)})
        )
        return run_log
