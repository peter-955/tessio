from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.shared_steps.models.shared_step_action_request import SharedStepActionRequest
from app.modules.shared_steps.typing.constants import MAX_SHARED_STEP_ACTIONS, MAX_SHARED_STEP_TITLE_LENGTH
from app.shared.common import WireModel


class UpdateSharedStepRequest(WireModel):
    base_version_number: int = Field(ge=1)
    title: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_SHARED_STEP_TITLE_LENGTH)]
        | None
    ) = None
    steps: list[SharedStepActionRequest] | None = Field(default=None, min_length=1, max_length=MAX_SHARED_STEP_ACTIONS)
    archived: bool | None = None
