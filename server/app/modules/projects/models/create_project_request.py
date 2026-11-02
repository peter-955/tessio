from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.modules.projects.typing.constants import PROJECT_KEY_PATTERN
from app.shared.common import WireModel


class CreateProjectRequest(WireModel):
    key: str = Field(pattern=PROJECT_KEY_PATTERN)
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    description: str | None = Field(default=None, max_length=2000)
    jira_project_key: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)] | None = (
        None
    )
    jira_board_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def require_both_jira_fields_or_none(self) -> CreateProjectRequest:
        if (self.jira_project_key is None) != (self.jira_board_id is None):
            raise ValueError("Give both the Jira project and the board, or neither.")
        return self
