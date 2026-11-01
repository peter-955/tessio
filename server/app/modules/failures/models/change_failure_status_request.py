from typing import Self

from pydantic import model_validator

from app.modules.failures.typing.enums import FailureStatus
from app.shared.common import WireModel


class ChangeFailureStatusRequest(WireModel):
    status: FailureStatus

    @model_validator(mode="after")
    def check_target_status(self) -> Self:
        if self.status is FailureStatus.OPEN:
            raise ValueError("A failure cannot be set back to open.")
        return self
