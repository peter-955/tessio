from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class SharedStepVersionTable(TableBase):
    __tablename__ = "shared_step_versions"
    __table_args__ = (UniqueConstraint("shared_step_id", "number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    shared_step_id: Mapped[UUID] = mapped_column(ForeignKey("shared_steps.id"))
    number: Mapped[int]
    steps: Mapped[JsonValue] = mapped_column(JSONB, nullable=False)
    data_keys: Mapped[list[str]] = mapped_column(ARRAY(String))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
