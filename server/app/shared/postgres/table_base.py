from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TableBase(DeclarativeBase):
    type_annotation_map: ClassVar[dict[type[datetime], DateTime]] = {datetime: DateTime(timezone=True)}

    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


def build_text_enum(enum_type: type[StrEnum], name: str) -> Enum:
    return Enum(
        enum_type,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=40,
        values_callable=lambda members: [member.value for member in members],
    )
