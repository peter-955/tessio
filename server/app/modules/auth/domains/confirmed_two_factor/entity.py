from app.modules.auth.domains.issued_session.entity import IssuedSession
from app.shared.common import Entity


class ConfirmedTwoFactor(Entity):
    issued_session: IssuedSession
    recovery_codes: list[str]
