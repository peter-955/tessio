from collections.abc import Mapping, Sequence
from datetime import datetime
from itertools import pairwise

from app.modules.test_cases.domains.decisive_result.entity import DecisiveResult
from app.modules.test_cases.typing.constants.flaky_case import (
    DISAGREEMENT_WINDOW,
    FLAKY_FLIP_THRESHOLD,
    FLAKY_RESULT_WINDOW,
    QUARANTINE_RELEASE_PASS_COUNT,
)
from app.modules.test_cases.typing.enums import ResultExecutorKind


def count_result_flips(results: Sequence[DecisiveResult]) -> int:
    window = results[:FLAKY_RESULT_WINDOW]
    return sum(1 for newer, older in pairwise(window) if newer.is_passed != older.is_passed)


def select_flaky_since(flaky_score: int, flaky_since: datetime | None, now: datetime) -> datetime | None:
    if flaky_score < FLAKY_FLIP_THRESHOLD:
        return None
    return flaky_since or now


def find_disagreed_at(latest_results: Mapping[ResultExecutorKind, DecisiveResult]) -> datetime | None:
    manual = latest_results.get(ResultExecutorKind.MANUAL)
    automated = latest_results.get(ResultExecutorKind.AUTOMATED)
    if manual is None or automated is None or manual.is_passed == automated.is_passed:
        return None
    if abs(manual.recorded_at - automated.recorded_at) > DISAGREEMENT_WINDOW:
        return None
    return max(manual.recorded_at, automated.recorded_at)


def is_quarantine_over(results_since_quarantine: Sequence[DecisiveResult]) -> bool:
    recent = results_since_quarantine[:QUARANTINE_RELEASE_PASS_COUNT]
    return len(recent) == QUARANTINE_RELEASE_PASS_COUNT and all(result.is_passed for result in recent)
