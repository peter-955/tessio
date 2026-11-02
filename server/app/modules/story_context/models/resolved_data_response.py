from app.shared.common import WireModel


class ResolvedDataResponse(WireModel):
    values: dict[str, str]
    unknown_keys: list[str]
