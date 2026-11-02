from pydantic import JsonValue

from app.modules.integrations.domains.chat_message.entity import ChatMessage
from app.modules.integrations.typing.constants import (
    CHAT_LINK_LABEL,
    TEAMS_CARD_CONTENT_TYPE,
    TEAMS_CARD_SCHEMA,
    TEAMS_CARD_VERSION,
)


def build_teams_payload(message: ChatMessage) -> dict[str, JsonValue]:
    body: list[JsonValue] = [
        {"type": "TextBlock", "text": message.title, "weight": "Bolder", "size": "Medium", "wrap": True}
    ]
    if message.text:
        body.append({"type": "TextBlock", "text": message.text, "wrap": True})
    if message.facts:
        facts: list[JsonValue] = [{"title": fact.label, "value": fact.value} for fact in message.facts]
        body.append({"type": "FactSet", "facts": facts})
    body.append({"type": "TextBlock", "text": message.footer, "isSubtle": True, "size": "Small", "wrap": True})
    card: dict[str, JsonValue] = {
        "$schema": TEAMS_CARD_SCHEMA,
        "type": "AdaptiveCard",
        "version": TEAMS_CARD_VERSION,
        "body": body,
        "actions": [{"type": "Action.OpenUrl", "title": CHAT_LINK_LABEL, "url": message.link_url}],
    }
    return {
        "type": "message",
        "attachments": [{"contentType": TEAMS_CARD_CONTENT_TYPE, "contentUrl": None, "content": card}],
    }
