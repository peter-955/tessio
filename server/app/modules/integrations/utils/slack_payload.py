from pydantic import JsonValue

from app.modules.integrations.domains.chat_message.entity import ChatMessage
from app.modules.integrations.typing.constants import (
    CHAT_LINK_LABEL,
    SLACK_FIELD_LIMIT,
    SLACK_HEADER_LIMIT,
    SLACK_MAX_FIELDS,
    SLACK_SECTION_LIMIT,
)
from app.modules.integrations.utils.chat_text import ELLIPSIS, shorten_chat_text


def escape_slack_text(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def shorten_slack_text(text: str, limit: int) -> str:
    stripped_text = text.strip()
    escaped_text = escape_slack_text(stripped_text)
    if len(escaped_text) <= limit:
        return escaped_text
    pieces: list[str] = []
    length = 0
    for character in stripped_text:
        piece = escape_slack_text(character)
        if length + len(piece) > limit - len(ELLIPSIS):
            break
        pieces.append(piece)
        length += len(piece)
    return "".join(pieces) + ELLIPSIS


def build_slack_payload(message: ChatMessage) -> dict[str, JsonValue]:
    blocks: list[JsonValue] = [
        {"type": "header", "text": {"type": "plain_text", "text": shorten_chat_text(message.title, SLACK_HEADER_LIMIT)}}
    ]
    if message.text:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": shorten_slack_text(message.text, SLACK_SECTION_LIMIT),
                },
            }
        )
    if message.facts:
        fields: list[JsonValue] = [
            {
                "type": "mrkdwn",
                "text": shorten_slack_text(f"*{fact.label}*\n{fact.value}", SLACK_FIELD_LIMIT),
            }
            for fact in message.facts[:SLACK_MAX_FIELDS]
        ]
        blocks.append({"type": "section", "fields": fields})
    blocks.append(
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": CHAT_LINK_LABEL}, "url": message.link_url}
            ],
        }
    )
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": escape_slack_text(message.footer)}]})
    return {"text": escape_slack_text(message.title), "blocks": blocks}
