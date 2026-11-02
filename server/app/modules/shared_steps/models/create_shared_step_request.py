from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.shared_steps.models.shared_step_action_request import SharedStepActionRequest
from app.modules.shared_steps.typing.constants import (
    MAX_SHARED_STEP_ACTIONS,
    MAX_SHARED_STEP_KEY_LENGTH,
    MAX_SHARED_STEP_TITLE_LENGTH,
)
from app.shared.common import WireModel


class CreateSharedStepRequest(WireModel):
    key: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_SHARED_STEP_KEY_LENGTH)]
    title: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_SHARED_STEP_TITLE_LENGTH)
    ]
    steps: list[SharedStepActionRequest] = Field(min_length=1, max_length=MAX_SHARED_STEP_ACTIONS)
