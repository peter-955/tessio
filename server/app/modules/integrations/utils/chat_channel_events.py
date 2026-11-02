from collections.abc import Iterable

from app.modules.integrations.typing.enums import IntegrationEvent


def order_chat_events(events: Iterable[IntegrationEvent]) -> list[IntegrationEvent]:
    chosen_events = set(events)
    return [event for event in IntegrationEvent if event in chosen_events]
