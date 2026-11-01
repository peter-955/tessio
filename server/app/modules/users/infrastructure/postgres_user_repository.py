from uuid import UUID

from sqlalchemy import func, or_, select, update

from app.modules.users.domains.user.entity import User
from app.modules.users.domains.user.repository import UserRepository
from app.modules.users.infrastructure.user_table import UserTable
from app.modules.users.typing.constants.search import LIKE_ESCAPE_CHARACTER
from app.modules.users.typing.enums import UserStatus, WorkspaceRole
from app.modules.users.utils.like_pattern import build_contains_pattern
from app.shared.postgres import Database


class PostgresUserRepository(UserRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, user_id: UUID) -> User | None:
        row = await self._database.get_current_session().get(UserTable, user_id)
        return None if row is None else User.model_validate(row)

    async def find_by_id_for_update(self, user_id: UUID) -> User | None:
        statement = (
            select(UserTable).where(UserTable.id == user_id).with_for_update().execution_options(populate_existing=True)
        )
        row = await self._database.get_current_session().scalar(statement)
        return None if row is None else User.model_validate(row)

    async def find_by_email(self, email: str) -> User | None:
        row = await self._database.get_current_session().scalar(select(UserTable).where(UserTable.email == email))
        return None if row is None else User.model_validate(row)

    async def add(self, user: User) -> None:
        session = self._database.get_current_session()
        session.add(UserTable(**user.model_dump()))
        await session.flush()

    async def update(self, current: User, updated: User) -> None:
        if current.id != updated.id:
            raise ValueError("A user can only be updated with its own id.")
        current_values = current.model_dump()
        changed_values = {
            field_name: value
            for field_name, value in updated.model_dump().items()
            if current_values[field_name] != value
        }
        if not changed_values:
            return
        await self._database.get_current_session().execute(
            update(UserTable).where(UserTable.id == current.id).values(**changed_values)
        )

    async def list(
        self, status: UserStatus | None, workspace_role: WorkspaceRole | None, query: str | None
    ) -> list[User]:
        statement = select(UserTable).order_by(func.lower(UserTable.name), UserTable.email)
        if status is not None:
            statement = statement.where(UserTable.status == status)
        if workspace_role is not None:
            statement = statement.where(UserTable.workspace_role == workspace_role)
        if query is not None:
            pattern = build_contains_pattern(query)
            statement = statement.where(
                or_(
                    UserTable.name.ilike(pattern, escape=LIKE_ESCAPE_CHARACTER),
                    UserTable.email.ilike(pattern, escape=LIKE_ESCAPE_CHARACTER),
                )
            )
        rows = await self._database.get_current_session().scalars(statement)
        return [User.model_validate(row) for row in rows]
