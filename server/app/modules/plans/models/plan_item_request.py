from typing import Self
from uuid import UUID

from pydantic import model_validator

from app.shared.common import WireModel


class PlanItemRequest(WireModel):
    suite_id: UUID | None = None
    story_id: UUID | None = None

    @model_validator(mode="after")
    def check_single_target(self) -> Self:
        if (self.suite_id is None) == (self.story_id is None):
            raise ValueError("Give exactly one of suiteId or storyId.")
        return self
