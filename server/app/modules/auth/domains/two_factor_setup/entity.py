from app.shared.common import Entity


class TwoFactorSetup(Entity):
    key: str
    setup_uri: str
