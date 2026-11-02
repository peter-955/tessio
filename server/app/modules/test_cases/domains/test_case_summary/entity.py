from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.modules.labels import Label
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.shared.common import Entity


class TestCaseSummary(Entity):
    test_case: TestCase
    story_key: str
    current_version_number: int
    step_count: int
    criterion_ids: list[UUID]
    last_saved_at: datetime
    labels: list[Label] = Field(default_factory=list)
