from uuid import UUID

from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.shared.common import WireModel


class RunReportStoryResponse(WireModel):
    story_id: UUID
    story_jira_key: str
    story_title: str
    counts: RunCountsResponse
