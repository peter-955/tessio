import math
from xml.etree.ElementTree import Element, ParseError

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import fromstring

from app.modules.runs.domains.junit_test.entity import JunitTest
from app.modules.runs.errors import JunitInvalidError
from app.modules.runs.typing.constants.junit import (
    CASE_CODE_PATTERN,
    JUNIT_CASE_PROPERTY,
    JUNIT_FAILED_TAGS,
    JUNIT_ROOT_TAGS,
    JUNIT_SKIPPED_TAG,
    MAX_JUNIT_DURATION_MS,
    MAX_JUNIT_MESSAGE_LENGTH,
    MAX_JUNIT_TESTS,
    MAX_JUNIT_TEXT_LENGTH,
)
from app.modules.runs.typing.enums import ResultStatus


def parse_junit(content: bytes) -> list[JunitTest]:
    root = read_root(content)
    if read_tag(root) not in JUNIT_ROOT_TAGS:
        raise JunitInvalidError("the root element must be <testsuites> or <testsuite>.")
    tests: list[JunitTest] = []
    for element in root.iter():
        if read_tag(element) != "testcase":
            continue
        if len(tests) >= MAX_JUNIT_TESTS:
            raise JunitInvalidError(f"the file has more than {MAX_JUNIT_TESTS} tests.")
        tests.append(build_junit_test(element))
    return tests


def read_root(content: bytes) -> Element:
    try:
        root: Element = fromstring(content, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except DefusedXmlException as error:
        raise JunitInvalidError("DTDs, entities and external references are not allowed.") from error
    except (ParseError, ValueError, LookupError) as error:
        raise JunitInvalidError("the XML is not well formed.") from error
    return root


def build_junit_test(element: Element) -> JunitTest:
    name = shorten(element.get("name", "").strip(), MAX_JUNIT_TEXT_LENGTH)
    classname = element.get("classname")
    status, message = read_outcome(element)
    return JunitTest(
        name=name,
        classname=None if classname is None else shorten(classname.strip(), MAX_JUNIT_TEXT_LENGTH),
        status=status,
        message=message,
        duration_ms=read_duration_ms(element.get("time")),
        case_numbers=find_case_numbers([*read_case_properties(element), element.get("name", "")]),
    )


def read_outcome(element: Element) -> tuple[ResultStatus, str | None]:
    for child in element:
        if read_tag(child) in JUNIT_FAILED_TAGS:
            return ResultStatus.FAILED, read_message(child)
    for child in element:
        if read_tag(child) == JUNIT_SKIPPED_TAG:
            return ResultStatus.SKIPPED, read_message(child)
    return ResultStatus.PASSED, None


def read_message(element: Element) -> str | None:
    message = (element.get("message") or "").strip() or (element.text or "").strip()
    return shorten(message, MAX_JUNIT_MESSAGE_LENGTH) if message else None


def read_case_properties(element: Element) -> list[str]:
    values: list[str] = []
    for child in element:
        if read_tag(child) != "properties":
            continue
        for property_element in child:
            if read_tag(property_element) == "property" and property_element.get("name") == JUNIT_CASE_PROPERTY:
                values.append(property_element.get("value") or property_element.text or "")
    return values


def find_case_numbers(texts: list[str]) -> list[int]:
    numbers: dict[int, None] = {}
    for text in texts:
        for match in CASE_CODE_PATTERN.finditer(text):
            numbers[int(match.group(1))] = None
    return list(numbers)


def read_duration_ms(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    if not math.isfinite(seconds) or seconds < 0 or seconds * 1000 > MAX_JUNIT_DURATION_MS:
        return None
    return round(seconds * 1000)


def read_tag(element: Element) -> str:
    return str(element.tag).rsplit("}", 1)[-1]


def shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"
