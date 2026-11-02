from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import Entity


class TestCaseVersion(Entity):
    id: UUID
    test_case_id: UUID
    number: int
    title: str
    priority: TestCasePriority
    business_value: str | None
    preconditions: str | None
    steps: list[TestStep]
    criterion_ids: list[UUID]
    data_keys: list[str]
    file_version_ids: list[UUID]
    created_by: UUID
    created_at: datetime
    parameters: list[str] = Field(default_factory=list)
    data_rows: list[dict[str, str]] = Field(default_factory=list)

    @property
    def iteration_count(self) -> int:
        return max(len(self.data_rows), 1)

    @property
    def shared_step_keys(self) -> list[str]:
        return list(
            dict.fromkeys(
                step.shared_step_key for step in self.steps if step.is_shared_step_reference and step.shared_step_key
            )
        )
