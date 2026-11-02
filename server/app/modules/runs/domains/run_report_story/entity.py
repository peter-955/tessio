from uuid import UUID

from app.modules.runs.domains.run_counts.entity import RunCounts
from app.shared.common import Entity


class RunReportStory(Entity):
    story_id: UUID
    story_jira_key: str
    story_title: str
    counts: RunCounts
