from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class AcceptanceCriterionTable(TableBase):
    __tablename__ = "acceptance_criteria"
    __table_args__ = (UniqueConstraint("story_id", "position"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    story_id: Mapped[UUID] = mapped_column(ForeignKey("stories.id"))
    position: Mapped[int]
    code: Mapped[str]
    text: Mapped[str] = mapped_column(Text)
    removed_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
