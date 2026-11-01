from app.modules.auth.typing.enums import SignInStep
from app.shared.common import Entity


class IssuedSession(Entity):
    token: str
    next_step: SignInStep
