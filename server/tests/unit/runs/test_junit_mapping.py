from datetime import UTC, datetime
from uuid import uuid7

from app.modules.runs.domains.import_case.entity import ImportCase
from app.modules.runs.domains.junit_test.entity import JunitTest
from app.modules.runs.typing.enums import ResultStatus, UnmappedTestReason
from app.modules.runs.utils.junit_mapping import map_junit_tests
from app.modules.test_cases import TestCaseVersion


def build_case(number: int) -> ImportCase:
    test_case_id = uuid7()
    version = TestCaseVersion.model_validate(
        {
            "id": uuid7(),
            "test_case_id": test_case_id,
            "number": 1,
            "title": f"Case {number}",
            "priority": "medium",
            "business_value": None,
            "preconditions": None,
            "steps": [{"order": 1, "action": "Open", "expected": "Opens"}],
            "criterion_ids": [],
            "data_keys": [],
            "file_version_ids": [],
            "created_by": uuid7(),
            "created_at": datetime.now(UTC),
        }
    )
    return ImportCase(test_case_id=test_case_id, number=number, story_id=uuid7(), version=version)


def build_test(
    name: str, numbers: list[int], status: ResultStatus, message: str | None = None, duration_ms: int = 100
) -> JunitTest:
    return JunitTest(
        name=name, classname=None, status=status, message=message, duration_ms=duration_ms, case_numbers=numbers
    )


def test_tests_of_one_case_are_combined_and_the_worst_outcome_wins() -> None:
    case = build_case(1)
    tests = [
        build_test("TC-1 desktop", [1], ResultStatus.PASSED),
        build_test("TC-1 mobile", [1], ResultStatus.FAILED, "Button hidden"),
        build_test("TC-1 tablet", [1], ResultStatus.FAILED, "Timeout"),
    ]

    outcomes, unmapped = map_junit_tests(tests, {1: case})

    assert unmapped == []
    assert len(outcomes) == 1
    assert outcomes[0].status is ResultStatus.FAILED
    assert outcomes[0].duration_ms == 300
    assert outcomes[0].error == "TC-1 mobile: Button hidden\n\nTC-1 tablet: Timeout"


def test_a_passed_and_a_skipped_test_pass_the_case() -> None:
    outcomes, _ = map_junit_tests(
        [build_test("a TC-2", [2], ResultStatus.SKIPPED), build_test("b TC-2", [2], ResultStatus.PASSED)],
        {2: build_case(2)},
    )

    assert outcomes[0].status is ResultStatus.PASSED
    assert outcomes[0].error is None


def test_tests_without_a_known_case_are_listed_with_a_reason() -> None:
    outcomes, unmapped = map_junit_tests(
        [
            build_test("no code here", [], ResultStatus.PASSED),
            build_test("TC-99 unknown", [99], ResultStatus.FAILED),
            build_test("TC-3 known and TC-98 unknown", [3, 98], ResultStatus.PASSED),
        ],
        {3: build_case(3)},
    )

    assert [outcome.case.number for outcome in outcomes] == [3]
    assert [(test.name, test.reason) for test in unmapped] == [
        ("no code here", UnmappedTestReason.NO_CASE_CODE),
        ("TC-99 unknown", UnmappedTestReason.UNKNOWN_CASE),
    ]


def test_the_combined_duration_of_a_case_is_capped_at_one_day() -> None:
    tests = [
        build_test("TC-3 first", [3], ResultStatus.PASSED, duration_ms=60_000_000),
        build_test("TC-3 second", [3], ResultStatus.PASSED, duration_ms=60_000_000),
    ]

    outcomes, _ = map_junit_tests(tests, {3: build_case(3)})

    assert outcomes[0].duration_ms == 86_400_000
