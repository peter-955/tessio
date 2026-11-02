from collections.abc import Collection, Sequence
from uuid import UUID

from pydantic import JsonValue

from app.modules.run_logs.domains.uploaded_run_log.entity import UploadedLogEntry
from app.modules.run_logs.typing.constants import BROWSER_TOOL_MARKERS, RECORD_CASE_RESULT_TOOL_SUFFIX
from app.modules.run_logs.typing.enums import RunLogEntryKind, RunLogPhase


def is_browser_action(entry: UploadedLogEntry) -> bool:
    tool = entry.tool or ""
    return entry.kind is RunLogEntryKind.ACTION and any(marker in tool for marker in BROWSER_TOOL_MARKERS)


def read_recorded_case_id(entry: UploadedLogEntry, case_ids: Collection[UUID]) -> UUID | None:
    tool = entry.tool or ""
    if entry.kind is not RunLogEntryKind.ACTION or not tool.endswith(RECORD_CASE_RESULT_TOOL_SUFFIX):
        return None
    raw_case_id: JsonValue = entry.input.get("case_id") if isinstance(entry.input, dict) else None
    try:
        case_id = UUID(str(raw_case_id))
    except ValueError:
        return None
    return case_id if case_id in case_ids else None


def find_setup_end(entries: Sequence[UploadedLogEntry], has_recorded_cases: bool) -> int:
    first_browser_index = next((index for index, entry in enumerate(entries) if is_browser_action(entry)), None)
    if first_browser_index is not None:
        return first_browser_index
    return 0 if has_recorded_cases else len(entries)


def assign_phases(
    entries: Sequence[UploadedLogEntry], case_ids: Collection[UUID]
) -> list[tuple[RunLogPhase, UUID | None]]:
    recorded_case_ids = [read_recorded_case_id(entry, case_ids) for entry in entries]
    last_case_index = max((index for index, case_id in enumerate(recorded_case_ids) if case_id), default=-1)
    setup_end = find_setup_end(entries, last_case_index >= 0)
    phases: list[tuple[RunLogPhase, UUID | None]] = [
        (RunLogPhase.SETUP if index < setup_end else RunLogPhase.WRAP_UP, None) for index in range(len(entries))
    ]
    pending: list[int] = []
    for index, case_id in enumerate(recorded_case_ids[: last_case_index + 1]):
        if index < setup_end and case_id is None:
            continue
        pending.append(index)
        if case_id is not None:
            for pending_index in pending:
                phases[pending_index] = (RunLogPhase.CASE, case_id)
            pending = []
    return phases
