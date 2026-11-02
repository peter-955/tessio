from datetime import datetime

from pydantic import Field, JsonValue

from app.modules.run_logs.typing.constants import MAX_RUN_LOG_ENTRIES, MAX_RUN_LOG_TOOL_LENGTH
from app.modules.run_logs.typing.enums import RunLogEntryKind
from app.shared.common import WireModel


class UploadedLogEntryRequest(WireModel):
    kind: RunLogEntryKind
    at: datetime
    text: str | None = None
    tool: str | None = Field(default=None, max_length=MAX_RUN_LOG_TOOL_LENGTH)
    input: JsonValue = None
    output: str | None = None
    is_error: bool = False
    duration_ms: int | None = Field(default=None, ge=0)


class RunLogUsageRequest(WireModel):
    input_tokens: int = Field(default=0, ge=0)
    cache_creation_input_tokens: int = Field(default=0, ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)


class UploadRunLogRequest(WireModel):
    is_cut: bool = False
    usage: RunLogUsageRequest = Field(default_factory=RunLogUsageRequest)
    entries: list[UploadedLogEntryRequest] = Field(max_length=MAX_RUN_LOG_ENTRIES)
