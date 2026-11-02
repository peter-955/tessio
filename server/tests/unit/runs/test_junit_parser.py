from pathlib import Path

import pytest

from app.modules.runs.errors import JunitInvalidError
from app.modules.runs.typing.enums import ResultStatus
from app.modules.runs.utils.junit_parser import find_case_numbers, parse_junit, read_duration_ms

JUNIT_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "junit"


def read_fixture(name: str) -> bytes:
    return (JUNIT_FIXTURES / name).read_bytes()


def test_a_playwright_report_is_read_with_names_properties_and_outcomes() -> None:
    tests = parse_junit(read_fixture("playwright.xml"))

    assert [(test.case_numbers, test.status) for test in tests] == [
        ([1], ResultStatus.PASSED),
        ([2], ResultStatus.FAILED),
        ([3], ResultStatus.PASSED),
        ([4], ResultStatus.SKIPPED),
        ([], ResultStatus.PASSED),
    ]
    assert tests[0].duration_ms == 3210
    assert tests[0].classname == "checkout.spec.ts"
    assert tests[1].message == "checkout.spec.ts:20:5 TC-2 refuses an expired card"


def test_a_jest_report_uses_the_failure_text_when_there_is_no_message() -> None:
    tests = parse_junit(read_fixture("jest.xml"))

    assert [(test.case_numbers, test.status) for test in tests] == [
        ([1], ResultStatus.PASSED),
        ([2], ResultStatus.FAILED),
        ([], ResultStatus.PASSED),
    ]
    assert tests[1].message is not None
    assert tests[1].message.startswith("Error: expect(received).toBe(expected)")
    assert 'Received: "Server error"' in tests[1].message


def test_a_pytest_report_maps_underscore_codes_properties_and_errors() -> None:
    tests = parse_junit(read_fixture("pytest.xml"))

    assert [(test.name, test.case_numbers, test.status) for test in tests] == [
        ("test_tc_1_creates_an_order", [1], ResultStatus.PASSED),
        ("test_cancels_an_order", [2], ResultStatus.FAILED),
        ("test_refund[TC-3]", [3], ResultStatus.FAILED),
        ("test_ships_later", [4], ResultStatus.SKIPPED),
        ("test_unrelated_helper", [], ResultStatus.PASSED),
    ]
    assert tests[1].message == "AssertionError: assert 'open' == 'cancelled'"
    assert tests[2].message == 'failed on setup with "ConnectionError: database is down"'
    assert tests[3].message == "Shipping is not ready"


@pytest.mark.parametrize("fixture_name", ["billion_laughs.xml", "external_entity.xml"])
def test_an_xml_bomb_or_external_entity_is_refused(fixture_name: str) -> None:
    with pytest.raises(JunitInvalidError) as raised:
        parse_junit(read_fixture(fixture_name))

    assert raised.value.code == "JUNIT_INVALID"


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"<testsuite><testcase name='TC-1'>",
        b"not xml at all",
        b"<html><body>TC-1</body></html>",
        b'<?xml version="1.0" encoding="foo-bar"?><testsuites/>',
        b'<?xml version="1.0" encoding="base64"?><testsuites/>',
        b'<?xml version="1.0" encoding="shift_jis"?><testsuites/>',
        b'<?xml version="1.0" encoding="utf-16"?><testsuites/>',
    ],
)
def test_content_that_is_not_junit_is_refused(content: bytes) -> None:
    with pytest.raises(JunitInvalidError):
        parse_junit(content)


def test_a_bare_testsuite_root_with_nested_suites_is_read() -> None:
    content = (
        b'<testsuites><testsuite name="a"><testsuite name="b">'
        b'<testcase name="TC-7 nested"><error message="boom"/></testcase>'
        b"</testsuite></testsuite></testsuites>"
    )

    tests = parse_junit(content)

    assert [(test.case_numbers, test.status, test.message) for test in tests] == [([7], ResultStatus.FAILED, "boom")]


def test_case_codes_are_found_in_several_spellings_and_only_once() -> None:
    assert find_case_numbers(["TC-12 and tc_13", "TC-12", "(TC-14)", "ATC-15", "TC-16x", "TC-1617"]) == [
        12,
        13,
        14,
        1617,
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.5", 1500),
        ("0", 0),
        ("86400", 86_400_000),
        ("86400.001", None),
        ("99999999", None),
        ("1e308", None),
        (None, None),
        ("abc", None),
        ("-1", None),
        ("nan", None),
        ("inf", None),
    ],
)
def test_durations_are_read_in_milliseconds(value: str | None, expected: int | None) -> None:
    assert read_duration_ms(value) == expected
