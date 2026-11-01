from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class ProjectTable(TableBase):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    description: Mapped[str | None]
    jira_project_key: Mapped[str] = mapped_column(unique=True)
    jira_board_id: Mapped[int]
    allowed_file_types: Mapped[list[str]] = mapped_column(ARRAY(String))
    archived_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
    default_environment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("environments.id", ondelete="SET NULL", name="fk_projects_default_environment_id", use_alter=True)
    )
