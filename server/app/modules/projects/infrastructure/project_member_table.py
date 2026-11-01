from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.permissions import ProjectRole
from app.shared.postgres import TableBase, build_text_enum


class ProjectMemberTable(TableBase):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[ProjectRole] = mapped_column(build_text_enum(ProjectRole, "project_role"))
    created_at: Mapped[datetime]
