from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class RunLog(Entity):
    run_id: UUID
    received_at: datetime
    is_cut: bool
    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int
