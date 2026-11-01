from app.modules.auth.typing.enums import SignInStep
from app.shared.common import WireModel


class RecoveryCodesResponse(WireModel):
    next_step: SignInStep
    recovery_codes: list[str]
