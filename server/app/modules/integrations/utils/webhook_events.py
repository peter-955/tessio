from collections.abc import Iterable

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent


def normalize_webhook_events(events: Iterable[IntegrationEvent]) -> list[IntegrationEvent]:
    chosen = set(events)
    return [event for event in IntegrationEvent if event in chosen]
