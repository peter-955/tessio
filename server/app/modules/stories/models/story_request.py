from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.stories.typing.constants import (
    MAX_STORY_CRITERIA,
    MAX_STORY_CRITERION_LENGTH,
    MAX_STORY_DESCRIPTION_LENGTH,
    MAX_STORY_TITLE_LENGTH,
)
from app.shared.common import WireModel


class StoryRequest(WireModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_STORY_TITLE_LENGTH)]
    description: str | None = Field(default=None, max_length=MAX_STORY_DESCRIPTION_LENGTH)
    criteria: list[
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_STORY_CRITERION_LENGTH)]
    ] = Field(default_factory=list, max_length=MAX_STORY_CRITERIA)
