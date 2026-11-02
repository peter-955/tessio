from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class StoryKeyCounterTable(TableBase):
    __tablename__ = "story_key_counters"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    last_number: Mapped[int]
    created_at: Mapped[datetime]
