from pydantic import Field

from app.shared.common import Entity


class SharedStepAction(Entity):
    order: int = Field(ge=1)
    action: str
    expected: str | None
