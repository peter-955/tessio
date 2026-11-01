from uuid import UUID

from app.modules.insights.domains.coverage_count.entity import CoverageCount
from app.modules.insights.domains.run_reference.entity import RunReference
from app.shared.common import Entity


class StoryProgress(Entity):
    story_id: UUID
    jira_key: str
    coverage: CoverageCount
    open_gap_count: int
    active_failure_count: int
    last_run: RunReference | None
