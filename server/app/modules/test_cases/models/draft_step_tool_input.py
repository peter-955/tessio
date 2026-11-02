from typing import Annotated

from pydantic import StringConstraints

from app.shared.common import ToolModel


class DraftStepToolInput(ToolModel):
    action: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    expected: Annotated[str, StringConstraints(strip_whitespace=True)] | None = None
