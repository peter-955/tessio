from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.run_logs.typing.enums import RunLogEntryKind, RunLogPhase
from app.shared.common import Entity


class RunLogEntry(Entity):
    id: UUID
    run_id: UUID
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
