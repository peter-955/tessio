from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.test_cases.typing.constants import MAX_SHARED_STEP_KEY_LENGTH, MAX_TEXT_LENGTH
from app.shared.common import WireModel


class TestStepRequest(WireModel):
    action: Annotated[str, StringConstraints(strip_whitespace=True, max_length=MAX_TEXT_LENGTH)] | None = None
    expected: str | None = Field(default=None, max_length=MAX_TEXT_LENGTH)
    shared_step_key: str | None = Field(default=None, max_length=MAX_SHARED_STEP_KEY_LENGTH)
