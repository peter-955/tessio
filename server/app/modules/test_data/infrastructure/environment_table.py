from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class EnvironmentTable(TableBase):
    __tablename__ = "environments"
    __table_args__ = (UniqueConstraint("project_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str]
    base_url: Mapped[str] = mapped_column(Text)
    health_check_url: Mapped[str | None] = mapped_column(Text)
    archived_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
