from app.modules.auth.typing.enums import SignInStep
from app.shared.common import WireModel


class SignInResponse(WireModel):
    next_step: SignInStep
