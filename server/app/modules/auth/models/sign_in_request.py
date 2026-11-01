from pydantic import Field

from app.shared.common import WireModel


class SignInRequest(WireModel):
    email: str = Field(max_length=320)
    password: str = Field(max_length=256)
