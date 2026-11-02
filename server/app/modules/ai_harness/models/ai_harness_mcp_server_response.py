from app.shared.common import WireModel


class AiHarnessMcpServerResponse(WireModel):
    name: str
    transport: str
    url: str
    header_names: list[str]
