import time
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import aclosing, asynccontextmanager
from datetime import timedelta
from uuid import UUID

from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventHub, LiveEventSubscription, LiveEventType
from app.shared.permissions import Actor, ProjectAccessResolver


class StreamLiveEventsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        hub: LiveEventHub,
        project_access_resolver: ProjectAccessResolver,
        refresh_interval: timedelta,
    ) -> None:
        self._transaction = transaction
        self._hub = hub
        self._project_access_resolver = project_access_resolver
        self._refresh_interval = refresh_interval

    @asynccontextmanager
    async def open_stream(self, actor: Actor) -> AsyncIterator[AsyncIterator[LiveEvent]]:
        async with self._hub.subscribe() as subscription:
            visible_project_ids = await self._load_visible_project_ids(actor)
            async with aclosing(self._filter_events(actor, subscription, visible_project_ids)) as events:
                yield events

    async def _filter_events(
        self, actor: Actor, subscription: LiveEventSubscription, visible_project_ids: frozenset[UUID]
    ) -> AsyncGenerator[LiveEvent]:
        loaded_at = time.monotonic()
        async for event in subscription:
            is_refresh_due = time.monotonic() - loaded_at >= self._refresh_interval.total_seconds()
            if is_refresh_due or event.type is LiveEventType.PROJECT_MEMBERS_CHANGED:
                visible_project_ids = await self._load_visible_project_ids(actor)
                loaded_at = time.monotonic()
            if self._is_visible(actor, event, visible_project_ids):
                yield event

    async def _load_visible_project_ids(self, actor: Actor) -> frozenset[UUID]:
        async with self._transaction.begin():
            return await self._project_access_resolver.list_visible_project_ids(actor)

    @staticmethod
    def _is_visible(actor: Actor, event: LiveEvent, visible_project_ids: frozenset[UUID]) -> bool:
        if event.user_id is not None:
            return event.user_id == actor.user_id
        if event.project_id is not None:
            return event.project_id in visible_project_ids
        return False
