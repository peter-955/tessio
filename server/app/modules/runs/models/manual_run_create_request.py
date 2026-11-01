from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from app.shared.common import WireModel


class ManualRunCreateRequest(WireModel):
    story_key: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
    environment_id: UUID | None = None
    test_case_ids: list[UUID] | None = Field(default=None, min_length=1, max_length=200)
