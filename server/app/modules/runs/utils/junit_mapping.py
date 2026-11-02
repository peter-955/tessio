from collections.abc import Mapping

from app.modules.runs.domains.import_case.entity import ImportCase
from app.modules.runs.domains.imported_case_outcome.entity import ImportedCaseOutcome
from app.modules.runs.domains.junit_test.entity import JunitTest
from app.modules.runs.domains.unmapped_test.entity import UnmappedTest
from app.modules.runs.typing.constants.junit import MAX_JUNIT_DURATION_MS, MAX_JUNIT_MESSAGE_LENGTH
from app.modules.runs.typing.enums import ResultStatus, UnmappedTestReason
from app.modules.runs.utils.junit_parser import shorten

IMPORT_STATUS_RANK = (ResultStatus.FAILED, ResultStatus.PASSED, ResultStatus.SKIPPED)


def map_junit_tests(
    tests: list[JunitTest], cases_by_number: Mapping[int, ImportCase]
) -> tuple[list[ImportedCaseOutcome], list[UnmappedTest]]:
    tests_by_number: dict[int, list[JunitTest]] = {}
    unmapped_tests: list[UnmappedTest] = []
    for test in tests:
        known_numbers = [number for number in test.case_numbers if number in cases_by_number]
        if not known_numbers:
            unmapped_tests.append(build_unmapped_test(test))
            continue
        for number in known_numbers:
            tests_by_number.setdefault(number, []).append(test)
    outcomes = [
        build_case_outcome(cases_by_number[number], case_tests) for number, case_tests in tests_by_number.items()
    ]
    return outcomes, unmapped_tests


def build_unmapped_test(test: JunitTest) -> UnmappedTest:
    return UnmappedTest(
        name=test.name,
        classname=test.classname,
        status=test.status,
        reason=UnmappedTestReason.UNKNOWN_CASE if test.case_numbers else UnmappedTestReason.NO_CASE_CODE,
    )


def build_case_outcome(case: ImportCase, tests: list[JunitTest]) -> ImportedCaseOutcome:
    status = min((test.status for test in tests), key=IMPORT_STATUS_RANK.index)
    durations = [test.duration_ms for test in tests if test.duration_ms is not None]
    return ImportedCaseOutcome(
        case=case,
        status=status,
        error=build_case_error(tests) if status is ResultStatus.FAILED else None,
        duration_ms=min(sum(durations), MAX_JUNIT_DURATION_MS) if durations else None,
    )


def build_case_error(tests: list[JunitTest]) -> str | None:
    failed_tests = [test for test in tests if test.status is ResultStatus.FAILED]
    if len(failed_tests) == 1:
        return failed_tests[0].message
    lines = [f"{test.name}: {test.message or 'failed'}" for test in failed_tests]
    return shorten("\n\n".join(lines), MAX_JUNIT_MESSAGE_LENGTH)
