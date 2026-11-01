from pydantic import Field

from app.shared.common import WireModel


class PasswordConfirmationRequest(WireModel):
    password: str = Field(max_length=256)
