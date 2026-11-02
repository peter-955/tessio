from pydantic import JsonValue

from app.modules.integrations.domains.chat_message.entity import ChatMessage
from app.modules.integrations.typing.enums import ChatChannelKind
from app.modules.integrations.utils.slack_payload import build_slack_payload
from app.modules.integrations.utils.teams_payload import build_teams_payload


def build_chat_payload(kind: ChatChannelKind, message: ChatMessage) -> dict[str, JsonValue]:
    match kind:
        case ChatChannelKind.SLACK:
            return build_slack_payload(message)
        case ChatChannelKind.TEAMS:
            return build_teams_payload(message)
