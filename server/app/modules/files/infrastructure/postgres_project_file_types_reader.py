from uuid import UUID

from sqlalchemy import ARRAY, String, Uuid, column, select, table

from app.modules.files.ports.project_file_types_reader import ProjectFileTypesReader
from app.shared.postgres import Database

PROJECTS = table("projects", column("id", Uuid()), column("allowed_file_types", ARRAY(String())))


class PostgresProjectFileTypesReader(ProjectFileTypesReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_allowed_file_types(self, project_id: UUID) -> list[str]:
        allowed_file_types = await self._database.get_current_session().scalar(
            select(PROJECTS.c.allowed_file_types).where(PROJECTS.c.id == project_id)
        )
        return [] if allowed_file_types is None else [str(file_type) for file_type in allowed_file_types]
