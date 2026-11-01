from app.modules.auth.domains.user_session.entity import UserSession
from app.modules.users import User
from app.shared.common import Entity


class AuthenticatedSession(Entity):
    user_session: UserSession
    user: User
