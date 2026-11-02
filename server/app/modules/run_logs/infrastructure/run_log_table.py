from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class RunLogTable(TableBase):
    __tablename__ = "run_logs"

    run_id: Mapped[UUID] = mapped_column(ForeignKey("runs.id"), primary_key=True)
    received_at: Mapped[datetime]
    is_cut: Mapped[bool]
    input_tokens: Mapped[int]
    cache_creation_input_tokens: Mapped[int]
    cache_read_input_tokens: Mapped[int]
    output_tokens: Mapped[int]
