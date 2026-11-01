from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from app.modules.projects.typing.constants import MIME_TYPE_PATTERN
from app.shared.common import WireModel


class UpdateProjectRequest(WireModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)] | None = None
    description: str | None = Field(default=None, max_length=2000)
    jira_board_id: int | None = Field(default=None, ge=1)
    allowed_file_types: list[Annotated[str, Field(pattern=MIME_TYPE_PATTERN, max_length=255)]] | None = Field(
        default=None, min_length=1, max_length=50
    )
    default_environment_id: UUID | None = None
