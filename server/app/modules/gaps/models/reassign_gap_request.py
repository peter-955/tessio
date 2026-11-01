from typing import Self
from uuid import UUID

from pydantic import model_validator

from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class ReassignGapRequest(WireModel):
    assignee_id: UUID | None = None
    assignee_role: ProjectRole | None = None

    @model_validator(mode="after")
    def check_single_assignee(self) -> Self:
        if (self.assignee_id is None) == (self.assignee_role is None):
            raise ValueError("Give exactly one of assigneeId or assigneeRole.")
        if self.assignee_role is ProjectRole.VIEWER:
            raise ValueError("Viewers cannot answer gaps.")
        return self
