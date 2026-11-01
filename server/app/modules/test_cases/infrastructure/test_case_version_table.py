from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.postgres import TableBase, build_text_enum


class TestCaseVersionTable(TableBase):
    __tablename__ = "test_case_versions"
    __table_args__ = (UniqueConstraint("test_case_id", "number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    number: Mapped[int]
    title: Mapped[str] = mapped_column(Text)
    priority: Mapped[TestCasePriority] = mapped_column(build_text_enum(TestCasePriority, "test_case_version_priority"))
    business_value: Mapped[str | None] = mapped_column(Text)
    preconditions: Mapped[str | None] = mapped_column(Text)
    steps: Mapped[JsonValue] = mapped_column(JSONB, nullable=False)
    criterion_ids: Mapped[list[UUID]] = mapped_column(ARRAY(Uuid))
    data_keys: Mapped[list[str]] = mapped_column(ARRAY(String))
    file_version_ids: Mapped[list[UUID]] = mapped_column(ARRAY(Uuid))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
