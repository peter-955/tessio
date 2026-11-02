from collections.abc import Collection, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.modules.notifications.domains.notification_preference.entity import NotificationPreference
from app.modules.notifications.domains.notification_preference.repository import NotificationPreferenceRepository
from app.modules.notifications.infrastructure.notification_preference_table import NotificationPreferenceTable
from app.modules.notifications.typing.enums import NotificationKind
from app.shared.postgres import Database


class PostgresNotificationPreferenceRepository(NotificationPreferenceRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_user(self, user_id: UUID) -> list[NotificationPreference]:
        rows = await self._database.get_current_session().scalars(
            select(NotificationPreferenceTable)
            .where(NotificationPreferenceTable.user_id == user_id)
            .order_by(NotificationPreferenceTable.kind, NotificationPreferenceTable.channel)
            .execution_options(populate_existing=True)
        )
        return [NotificationPreference.model_validate(row) for row in rows]

    async def list_for_users(self, user_ids: Collection[UUID], kind: NotificationKind) -> list[NotificationPreference]:
        if not user_ids:
            return []
        rows = await self._database.get_current_session().scalars(
            select(NotificationPreferenceTable)
            .where(NotificationPreferenceTable.user_id.in_(sorted(user_ids)), NotificationPreferenceTable.kind == kind)
            .execution_options(populate_existing=True)
        )
        return [NotificationPreference.model_validate(row) for row in rows]

    async def save_all(self, preferences: Sequence[NotificationPreference]) -> None:
        if not preferences:
            return
        statement = insert(NotificationPreferenceTable).values([preference.model_dump() for preference in preferences])
        await self._database.get_current_session().execute(
            statement.on_conflict_do_update(
                index_elements=["user_id", "kind", "channel"],
                set_={"is_enabled": statement.excluded.is_enabled, "updated_at": func.now()},
            )
        )
