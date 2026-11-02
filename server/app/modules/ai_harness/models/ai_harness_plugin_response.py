from app.shared.common import WireModel


class AiHarnessPluginResponse(WireModel):
    name: str
    version: str
    description: str
    update_command: str
