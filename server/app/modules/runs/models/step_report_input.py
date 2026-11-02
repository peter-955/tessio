from typing import Annotated

from pydantic import Field

from app.modules.runs.models.failed_request_input import FailedRequestInput
from app.modules.runs.typing.constants.run import (
    MAX_DIAGNOSIS_ITEMS,
    MAX_DIAGNOSIS_TEXT_LENGTH,
    MAX_PAGE_URL_LENGTH,
)
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import ToolModel


class StepReportInput(ToolModel):
    order: int = Field(ge=1)
    status: ResultStatus
    actual_result: str = Field(max_length=4000)
    error: str | None = Field(default=None, max_length=4000)
    screenshot_path: str | None = Field(default=None, max_length=1024)
    page_url: str | None = Field(default=None, max_length=MAX_PAGE_URL_LENGTH)
    console_errors: list[Annotated[str, Field(max_length=MAX_DIAGNOSIS_TEXT_LENGTH)]] = Field(
        default_factory=list, max_length=MAX_DIAGNOSIS_ITEMS
    )
    failed_requests: list[FailedRequestInput] = Field(default_factory=list, max_length=MAX_DIAGNOSIS_ITEMS)
