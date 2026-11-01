from app.shared.common import WireModel


class RecoveryCodeListResponse(WireModel):
    recovery_codes: list[str]
