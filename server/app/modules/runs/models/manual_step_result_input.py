from uuid import UUID

from pydantic import Field

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import WireModel


class ManualStepResultInput(WireModel):
    order: int = Field(ge=1)
    status: ResultStatus
    actual_result: str = Field(default="", max_length=4000)
    error: str | None = Field(default=None, max_length=4000)
    evidence_file_id: UUID | None = None
