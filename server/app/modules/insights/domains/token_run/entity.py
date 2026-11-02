from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class TokenRun(Entity):
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
    is_cut: bool

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.cache_creation_input_tokens + self.cache_read_input_tokens + self.output_tokens
