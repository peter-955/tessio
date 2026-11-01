from pydantic import Field

from app.shared.common import WireModel


class ForgotPasswordRequest(WireModel):
    email: str = Field(max_length=320)
