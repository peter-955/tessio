from datetime import datetime
from uuid import UUID

from app.shared.common import WireModel


class TokenRunResponse(WireModel):
    run_id: UUID
    started_at: datetime
    executor: str
    story_jira_key: str | None
    test_suite_name: str | None
    case_count: int
    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int
    total_tokens: int
    tokens_per_case: int | None
    is_cut: bool
