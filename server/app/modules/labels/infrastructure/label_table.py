from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.labels.typing.enums import LabelColor
from app.shared.postgres import TableBase, build_text_enum


class LabelTable(TableBase):
    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("project_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(Text)
    color: Mapped[LabelColor] = mapped_column(build_text_enum(LabelColor, "label_color"))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
