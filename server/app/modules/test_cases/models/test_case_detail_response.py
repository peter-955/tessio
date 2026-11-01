from datetime import datetime
from uuid import UUID

from app.modules.test_cases.models.case_story_response import CaseStoryResponse
from app.modules.test_cases.models.linked_criterion_response import LinkedCriterionResponse
from app.modules.test_cases.models.test_case_version_response import TestCaseVersionResponse
from app.modules.test_cases.models.test_file_response import TestFileResponse
from app.modules.test_cases.typing.enums import TestCasePriority, TestCaseStatus
from app.shared.common import WireModel


class TestCaseDetailResponse(WireModel):
    id: UUID
    code: str
    story: CaseStoryResponse
    title: str
    priority: TestCasePriority
    status: TestCaseStatus
    status_changed_at: datetime | None
    current_version: TestCaseVersionResponse
    criteria: list[LinkedCriterionResponse]
    files: list[TestFileResponse]
    unknown_references: list[str]
    needs_review: bool
    needs_review_criterion_ids: list[UUID]
    needs_review_at: datetime | None
    reviewed_at: datetime | None
    reviewed_by: UUID | None
    created_by: UUID
    created_at: datetime
