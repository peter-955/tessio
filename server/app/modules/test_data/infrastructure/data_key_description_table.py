from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class DataKeyDescriptionTable(TableBase):
    __tablename__ = "test_data_descriptions"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    key: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text)
