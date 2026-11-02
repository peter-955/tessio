from datetime import date, datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class ProjectDailyStatsTable(TableBase):
    __tablename__ = "project_daily_stats"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    day: Mapped[date] = mapped_column(primary_key=True)
    runs_by_executor: Mapped[dict[str, int]] = mapped_column(JSONB)
    passed_count: Mapped[int]
    failed_count: Mapped[int]
    blocked_count: Mapped[int]
    skipped_count: Mapped[int]
    failures_opened: Mapped[int]
    failures_fixed: Mapped[int]
    fix_seconds_total: Mapped[int] = mapped_column(BigInteger)
    gaps_opened: Mapped[int]
    gaps_answered: Mapped[int]
    answer_seconds_total: Mapped[int] = mapped_column(BigInteger)
    open_gap_count: Mapped[int]
    median_open_gap_age_seconds: Mapped[int | None] = mapped_column(BigInteger)
    computed_at: Mapped[datetime]
