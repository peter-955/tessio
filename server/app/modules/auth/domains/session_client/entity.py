from app.shared.common import Entity


class SessionClient(Entity):
    user_agent: str | None
    ip: str | None
