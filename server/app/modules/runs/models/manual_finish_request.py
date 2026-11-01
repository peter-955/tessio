from pydantic import Field

from app.shared.common import WireModel


class ManualFinishRequest(WireModel):
    summary: str | None = Field(default=None, max_length=4000)
