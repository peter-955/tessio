from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.run_logs.typing.enums import RunLogEntryKind, RunLogPhase
from app.shared.common import WireModel


class RunLogEntryResponse(WireModel):
    position: int
    phase: RunLogPhase
    test_case_id: UUID | None
    kind: RunLogEntryKind
    at: datetime
    tool: str | None
    input: JsonValue
    output: str | None
    is_error: bool
    duration_ms: int | None


class RunLogUsageResponse(WireModel):
    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int


class RunLogResponse(WireModel):
    received_at: datetime | None
    is_cut: bool
    usage: RunLogUsageResponse | None
    entries: list[RunLogEntryResponse]


class RunLogReceiptResponse(WireModel):
    received_at: datetime
    entry_count: int
