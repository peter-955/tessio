from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update

from app.modules.api_tokens.domains.api_token.entity import ApiToken
from app.modules.api_tokens.domains.api_token.repository import ApiTokenRepository
from app.modules.api_tokens.domains.api_token_summary.entity import ApiTokenSummary
from app.modules.api_tokens.infrastructure.api_token_table import ApiTokenTable
from app.modules.projects.infrastructure import ProjectTable
from app.shared.postgres import Database


class PostgresApiTokenRepository(ApiTokenRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_token_hash(self, token_hash: str) -> ApiToken | None:
        row = await self._database.get_current_session().scalar(
            select(ApiTokenTable).where(ApiTokenTable.token_hash == token_hash)
        )
        return None if row is None else ApiToken.model_validate(row)

    async def find_by_id(self, token_id: UUID) -> ApiToken | None:
        row = await self._database.get_current_session().get(ApiTokenTable, token_id)
        return None if row is None else ApiToken.model_validate(row)

    async def count_active_for_user(self, user_id: UUID, now: datetime) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(ApiTokenTable)
            .where(
                ApiTokenTable.user_id == user_id,
                ApiTokenTable.revoked_at.is_(None),
                ApiTokenTable.expires_at > now,
            )
        )
        return count or 0

    async def list_summaries_for_user(self, user_id: UUID) -> list[ApiTokenSummary]:
        result = await self._database.get_current_session().execute(
            select(ApiTokenTable, ProjectTable.key, ProjectTable.name)
            .join(ProjectTable, ProjectTable.id == ApiTokenTable.project_id)
            .where(ApiTokenTable.user_id == user_id)
            .order_by(ApiTokenTable.created_at.desc(), ApiTokenTable.id.desc())
        )
        return [
            ApiTokenSummary(api_token=ApiToken.model_validate(row), project_key=project_key, project_name=project_name)
            for row, project_key, project_name in result
        ]

    async def save(self, api_token: ApiToken) -> None:
        await self._database.get_current_session().merge(ApiTokenTable(**api_token.model_dump()))

    async def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None:
        await self._database.get_current_session().execute(
            update(ApiTokenTable)
            .where(ApiTokenTable.user_id == user_id, ApiTokenTable.revoked_at.is_(None))
            .values(revoked_at=now)
        )
