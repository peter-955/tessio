from pydantic import Field

from app.modules.runs.typing.constants.run import MAX_DIAGNOSIS_TEXT_LENGTH, MAX_PAGE_URL_LENGTH
from app.shared.common import ToolModel


class FailedRequestInput(ToolModel):
    method: str = Field(min_length=1, max_length=10)
    path: str = Field(min_length=1, max_length=MAX_PAGE_URL_LENGTH)
    status: int = Field(ge=0, le=999)
    excerpt: str | None = Field(default=None, max_length=MAX_DIAGNOSIS_TEXT_LENGTH)
