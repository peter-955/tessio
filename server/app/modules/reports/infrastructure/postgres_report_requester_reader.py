from uuid import UUID

from sqlalchemy import select

from app.modules.reports.domains.report_requester.entity import ReportRequester
from app.modules.reports.ports.report_requester_reader import ReportRequesterReader
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresReportRequesterReader(ReportRequesterReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_requester(self, user_id: UUID) -> ReportRequester | None:
        row = await self._database.get_current_session().scalar(select(UserTable).where(UserTable.id == user_id))
        if row is None:
            return None
        return ReportRequester(
            user_id=row.id,
            workspace_role=row.workspace_role,
            language=row.language,
            is_active=row.status is UserStatus.ACTIVE and row.deactivated_at is None,
        )
