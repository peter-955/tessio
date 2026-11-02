from app.shared.common import WireModel


class AiHarnessSlashCommandResponse(WireModel):
    name: str
    command: str
    argument_hint: str | None
    description: str
