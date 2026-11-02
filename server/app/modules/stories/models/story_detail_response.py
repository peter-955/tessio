from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.stories.models.acceptance_criterion_response import AcceptanceCriterionResponse
from app.modules.stories.models.sprint_reference_response import SprintReferenceResponse
from app.modules.stories.typing.enums import StorySource, TestStatus
from app.shared.common import WireModel


class StoryDetailResponse(WireModel):
    id: UUID
    jira_key: str
    jira_url: str
    title: str
    jira_status: str
    jira_issue_type: str
    test_status: TestStatus
    synced_at: datetime
    jira_missing_at: datetime | None
    description: JsonValue
    sprint: SprintReferenceResponse | None
    criteria: list[AcceptanceCriterionResponse]
    available_test_statuses: list[TestStatus]
    test_status_changed_at: datetime | None
    jira_updated_at: datetime
    source: StorySource
    description_text: str | None
