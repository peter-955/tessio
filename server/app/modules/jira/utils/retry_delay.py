import math
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from app.modules.jira.typing.constants import JIRA_DEFAULT_RETRY_DELAY_SECONDS, JIRA_MAX_RETRY_DELAY_SECONDS


def compute_retry_delay(retry_after: str | None, attempt: int, now: datetime) -> float:
    requested_delay = parse_retry_after(retry_after, now)
    if requested_delay is None:
        requested_delay = JIRA_DEFAULT_RETRY_DELAY_SECONDS * 2**attempt
    return min(max(requested_delay, 0.0), JIRA_MAX_RETRY_DELAY_SECONDS)


def parse_retry_after(retry_after: str | None, now: datetime) -> float | None:
    if retry_after is None or not retry_after.strip():
        return None
    stripped_retry_after = retry_after.strip()
    try:
        seconds = float(stripped_retry_after)
    except ValueError:
        return _parse_retry_at(stripped_retry_after, now)
    return seconds if math.isfinite(seconds) else None


def _parse_retry_at(retry_after: str, now: datetime) -> float | None:
    try:
        retry_at = parsedate_to_datetime(retry_after)
    except TypeError, ValueError:
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=UTC)
    return (retry_at - now).total_seconds()
