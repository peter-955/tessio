from datetime import date, datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.plans.typing.constants import PLAN_STATUS_CONSTRAINT
from app.modules.plans.typing.enums import PlanStatus
from app.shared.postgres import TableBase, build_text_enum


class TestPlanTable(TableBase):
    __tablename__ = "test_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    target_date: Mapped[date | None]
    environment_id: Mapped[UUID | None] = mapped_column(ForeignKey("environments.id"))
    status: Mapped[PlanStatus] = mapped_column(build_text_enum(PlanStatus, PLAN_STATUS_CONSTRAINT))
    signed_off_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    signed_off_at: Mapped[datetime | None]
    closed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    closed_at: Mapped[datetime | None]
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
