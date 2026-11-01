from pydantic import Field

from app.shared.common import WireModel


class ChangePasswordRequest(WireModel):
    current_password: str = Field(max_length=256)
    new_password: str = Field(max_length=256)
