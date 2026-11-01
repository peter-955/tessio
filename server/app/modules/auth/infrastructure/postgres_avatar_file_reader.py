from uuid import UUID

from sqlalchemy import select

from app.modules.auth.domains.avatar_file.entity import AvatarFile
from app.modules.auth.infrastructure.stored_file_view import STORED_FILE_VIEW
from app.modules.auth.ports.avatar_file_reader import AvatarFileReader
from app.modules.auth.typing.constants.avatar_file import AVATAR_FILE_KIND, UPLOADED_FILE_STATUS
from app.shared.postgres import Database


class PostgresAvatarFileReader(AvatarFileReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, file_id: UUID) -> AvatarFile | None:
        result = await self._database.get_current_session().execute(
            select(
                STORED_FILE_VIEW.c.id,
                STORED_FILE_VIEW.c.uploaded_by,
                STORED_FILE_VIEW.c.object_key,
                STORED_FILE_VIEW.c.file_name,
                STORED_FILE_VIEW.c.status,
            ).where(STORED_FILE_VIEW.c.id == file_id, STORED_FILE_VIEW.c.kind == AVATAR_FILE_KIND)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return AvatarFile(
            id=row.id,
            uploaded_by=row.uploaded_by,
            object_key=row.object_key,
            file_name=row.file_name,
            is_uploaded=row.status == UPLOADED_FILE_STATUS,
        )
