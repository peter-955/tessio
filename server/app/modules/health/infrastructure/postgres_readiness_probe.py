from sqlalchemy import text

from app.modules.health.ports.dependency_probe import DependencyProbe
from app.shared.postgres import Database


class PostgresReadinessProbe(DependencyProbe):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_reachable(self) -> bool:
        async with self._database.begin():
            await self._database.get_current_session().execute(text("SELECT 1"))
        return True
