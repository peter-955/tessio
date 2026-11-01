from pydantic import Field

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import ToolModel


class StepReportInput(ToolModel):
    order: int = Field(ge=1)
    status: ResultStatus
    actual_result: str = Field(max_length=4000)
    error: str | None = Field(default=None, max_length=4000)
    screenshot_path: str | None = Field(default=None, max_length=1024)
