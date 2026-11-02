from datetime import UTC, datetime, timedelta
from uuid import uuid7

import pytest

from app.modules.test_cases import DecisiveResult, ResultExecutorKind
from app.modules.test_cases.utils.flaky_case import (
    count_result_flips,
    find_disagreed_at,
    is_quarantine_over,
    select_flaky_since,
)

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)
VERSION_ID = uuid7()


def build_result(
    is_passed: bool,
    minutes_ago: int = 0,
    executor_kind: ResultExecutorKind = ResultExecutorKind.AUTOMATED,
) -> DecisiveResult:
    return DecisiveResult(
        case_result_id=uuid7(),
        test_case_version_id=VERSION_ID,
        is_passed=is_passed,
        executor_kind=executor_kind,
        recorded_at=NOW - timedelta(minutes=minutes_ago),
    )


def build_history(outcomes: str) -> list[DecisiveResult]:
    return [build_result(outcome == "P", minutes_ago=index) for index, outcome in enumerate(outcomes)]


@pytest.mark.parametrize(
    ("outcomes", "flips"),
    [
        ("", 0),
        ("P", 0),
        ("PF", 1),
        ("PFP", 2),
        ("PFPF", 3),
        ("PPPPPPPPPP", 0),
        ("PFPPPPPPPF", 3),
        ("PFPFPFPFPF", 9),
        ("PPPPPPPPPPFPFP", 0),
        ("PPPPPPPPPF" + "PFPF", 1),
    ],
)
def test_flips_are_counted_in_the_last_ten_results_only(outcomes: str, flips: int) -> None:
    assert count_result_flips(build_history(outcomes)) == flips


def test_two_results_can_never_be_flaky() -> None:
    flaky_score = count_result_flips(build_history("PF"))

    assert select_flaky_since(flaky_score, None, NOW) is None


def test_three_results_can_never_be_flaky() -> None:
    flaky_score = count_result_flips(build_history("PFP"))

    assert select_flaky_since(flaky_score, None, NOW) is None


def test_three_flips_make_a_case_flaky_from_now() -> None:
    flaky_score = count_result_flips(build_history("PFPF"))

    assert select_flaky_since(flaky_score, None, NOW) == NOW


def test_a_flaky_case_keeps_the_time_it_became_flaky() -> None:
    became_flaky_at = NOW - timedelta(days=3)

    assert select_flaky_since(5, became_flaky_at, NOW) == became_flaky_at


def test_a_case_below_three_flips_is_no_longer_flaky() -> None:
    assert select_flaky_since(2, NOW - timedelta(days=3), NOW) is None


def test_manual_and_automated_results_that_differ_within_a_day_disagree() -> None:
    manual = build_result(True, minutes_ago=60, executor_kind=ResultExecutorKind.MANUAL)
    automated = build_result(False, minutes_ago=30, executor_kind=ResultExecutorKind.AUTOMATED)

    disagreed_at = find_disagreed_at({ResultExecutorKind.MANUAL: manual, ResultExecutorKind.AUTOMATED: automated})

    assert disagreed_at == automated.recorded_at


def test_results_exactly_one_day_apart_still_disagree() -> None:
    manual = build_result(False, minutes_ago=24 * 60, executor_kind=ResultExecutorKind.MANUAL)
    automated = build_result(True, minutes_ago=0, executor_kind=ResultExecutorKind.AUTOMATED)

    disagreed_at = find_disagreed_at({ResultExecutorKind.MANUAL: manual, ResultExecutorKind.AUTOMATED: automated})

    assert disagreed_at == NOW


def test_results_more_than_one_day_apart_do_not_disagree() -> None:
    manual = build_result(False, minutes_ago=24 * 60 + 1, executor_kind=ResultExecutorKind.MANUAL)
    automated = build_result(True, minutes_ago=0, executor_kind=ResultExecutorKind.AUTOMATED)

    assert find_disagreed_at({ResultExecutorKind.MANUAL: manual, ResultExecutorKind.AUTOMATED: automated}) is None


def test_results_that_agree_do_not_disagree() -> None:
    manual = build_result(False, minutes_ago=10, executor_kind=ResultExecutorKind.MANUAL)
    automated = build_result(False, minutes_ago=0, executor_kind=ResultExecutorKind.AUTOMATED)

    assert find_disagreed_at({ResultExecutorKind.MANUAL: manual, ResultExecutorKind.AUTOMATED: automated}) is None


@pytest.mark.parametrize("executor_kind", list(ResultExecutorKind))
def test_one_kind_of_executor_alone_never_disagrees(executor_kind: ResultExecutorKind) -> None:
    assert find_disagreed_at({executor_kind: build_result(False, executor_kind=executor_kind)}) is None


def test_ten_passes_in_a_row_end_quarantine() -> None:
    assert is_quarantine_over(build_history("P" * 10)) is True


def test_nine_passes_do_not_end_quarantine() -> None:
    assert is_quarantine_over(build_history("P" * 9)) is False


def test_a_failure_among_the_last_ten_keeps_quarantine() -> None:
    assert is_quarantine_over(build_history("PPPPPPPPPF")) is False


def test_older_failures_before_ten_passes_do_not_keep_quarantine() -> None:
    assert is_quarantine_over(build_history("P" * 10 + "F")) is True
