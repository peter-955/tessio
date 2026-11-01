from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.projects.typing.constants import PROJECT_KEY_PATTERN
from app.shared.common import WireModel


class CreateProjectRequest(WireModel):
    key: str = Field(pattern=PROJECT_KEY_PATTERN)
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    description: str | None = Field(default=None, max_length=2000)
    jira_project_key: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
    jira_board_id: int = Field(ge=1)
