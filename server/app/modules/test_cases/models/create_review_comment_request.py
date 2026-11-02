from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.test_cases.typing.constants import MAX_REVIEW_COMMENT_LENGTH, MAX_STEPS
from app.shared.common import WireModel


class CreateReviewCommentRequest(WireModel):
    body: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_REVIEW_COMMENT_LENGTH)]
    step_order: int | None = Field(default=None, ge=1, le=MAX_STEPS)
    version_number: int | None = Field(default=None, ge=1)
