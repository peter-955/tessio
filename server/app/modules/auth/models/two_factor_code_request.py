from pydantic import Field

from app.shared.common import WireModel


class TwoFactorCodeRequest(WireModel):
    code: str = Field(max_length=32)
