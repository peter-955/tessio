from datetime import UTC, date, datetime

from app.modules.reports.typing.constants import EMPTY_CELL, REPORT_TEXTS, VALUE_LABELS
from app.modules.reports.typing.enums import ReportText
from app.modules.users import UserLanguage


def translate(language: UserLanguage, key: ReportText) -> str:
    return REPORT_TEXTS[language][key]


def label_value(language: UserLanguage, value: str | None) -> str:
    if value is None:
        return EMPTY_CELL
    return VALUE_LABELS[language].get(value, value)


def format_moment(moment: datetime | None) -> str:
    if moment is None:
        return EMPTY_CELL
    return moment.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def format_day(day: date | None) -> str:
    return EMPTY_CELL if day is None else day.isoformat()


def format_duration(started_at: datetime, finished_at: datetime | None) -> str:
    if finished_at is None:
        return EMPTY_CELL
    total_seconds = max(round((finished_at - started_at).total_seconds()), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def format_optional(text: str | None) -> str:
    return EMPTY_CELL if text is None or not text.strip() else text
