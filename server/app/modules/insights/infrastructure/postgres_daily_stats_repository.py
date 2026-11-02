from collections.abc import Sequence
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.insights.domains.daily_stats.repository import DailyStatsRepository
from app.modules.insights.infrastructure.project_daily_stats_table import ProjectDailyStatsTable
from app.shared.postgres import Database


class PostgresDailyStatsRepository(DailyStatsRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_between(self, project_id: UUID, first_day: date, last_day: date) -> list[DailyStats]:
        rows = await self._database.get_current_session().scalars(
            select(ProjectDailyStatsTable)
            .where(
                ProjectDailyStatsTable.project_id == project_id,
                ProjectDailyStatsTable.day >= first_day,
                ProjectDailyStatsTable.day <= last_day,
            )
            .order_by(ProjectDailyStatsTable.day)
        )
        return [
            DailyStats(
                project_id=row.project_id,
                day=row.day,
                runs_by_executor=dict(row.runs_by_executor),
                passed_count=row.passed_count,
                failed_count=row.failed_count,
                blocked_count=row.blocked_count,
                skipped_count=row.skipped_count,
                failures_opened=row.failures_opened,
                failures_fixed=row.failures_fixed,
                fix_seconds_total=row.fix_seconds_total,
                gaps_opened=row.gaps_opened,
                gaps_answered=row.gaps_answered,
                answer_seconds_total=row.answer_seconds_total,
                open_gap_count=row.open_gap_count,
                median_open_gap_age_seconds=row.median_open_gap_age_seconds,
            )
            for row in rows
        ]

    async def save_all(self, stats: Sequence[DailyStats], computed_at: datetime) -> None:
        if not stats:
            return
        values = [
            {**day_stats.model_dump(), "computed_at": computed_at, "updated_at": computed_at} for day_stats in stats
        ]
        statement = insert(ProjectDailyStatsTable).values(values)
        updated_columns = {
            column.name: statement.excluded[column.name]
            for column in ProjectDailyStatsTable.__table__.columns
            if column.name not in {"project_id", "day"}
        }
        await self._database.get_current_session().execute(
            statement.on_conflict_do_update(index_elements=["project_id", "day"], set_=updated_columns)
        )
