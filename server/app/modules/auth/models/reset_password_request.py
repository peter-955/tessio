from pydantic import Field

from app.shared.common import WireModel


class ResetPasswordRequest(WireModel):
    token: str = Field(max_length=128)
    password: str = Field(max_length=256)
