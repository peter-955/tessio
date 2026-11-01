from app.shared.common import WireModel


class TwoFactorSetupResponse(WireModel):
    key: str
    setup_uri: str
