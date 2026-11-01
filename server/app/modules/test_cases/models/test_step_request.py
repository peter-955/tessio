from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.test_cases.typing.constants import MAX_TEXT_LENGTH
from app.shared.common import WireModel


class TestStepRequest(WireModel):
    action: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_TEXT_LENGTH)]
    expected: str | None = Field(default=None, max_length=MAX_TEXT_LENGTH)
