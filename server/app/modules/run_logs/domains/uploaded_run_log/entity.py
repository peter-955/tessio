from datetime import datetime

from pydantic import JsonValue

from app.modules.run_logs.typing.enums import RunLogEntryKind
from app.shared.common import Entity


class UploadedLogEntry(Entity):
    kind: RunLogEntryKind
    at: datetime
    text: str | None = None
    tool: str | None = None
    input: JsonValue = None
    output: str | None = None
    is_error: bool = False
    duration_ms: int | None = None


class UploadedRunLog(Entity):
    is_cut: bool
    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int
    entries: list[UploadedLogEntry]
