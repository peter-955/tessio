from pydantic import Field

from app.shared.common import WireModel


class AcceptInviteRequest(WireModel):
    password: str = Field(max_length=256)
