from pydantic import Field

from app.shared.common import Entity


class TestStep(Entity):
    order: int = Field(ge=1)
    action: str
    expected: str | None
