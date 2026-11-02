from pydantic import Field

from app.shared.common import Entity


class ChatFact(Entity):
    label: str
    value: str


class ChatMessage(Entity):
    title: str
    text: str | None
    facts: list[ChatFact] = Field(default_factory=list)
    link_url: str
    footer: str
