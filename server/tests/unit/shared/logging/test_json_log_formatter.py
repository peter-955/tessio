import json
import logging
import sys
from datetime import datetime

from app.shared.logging import JsonLogFormatter


class Unserializable:
    def __str__(self) -> str:
        return "unserializable value"


def build_record(message: str, extra: dict[str, object], is_failure: bool = False) -> logging.LogRecord:
    exception_info = None
    if is_failure:
        try:
            raise ValueError("boom")
        except ValueError:
            exception_info = sys.exc_info()
    record = logging.LogRecord("tessio.test", logging.WARNING, __file__, 1, message, None, exception_info)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_formats_a_record_as_one_json_line() -> None:
    record = build_record("readiness.check_failed", {"dependency": "redis"})

    line = JsonLogFormatter().format(record)
    entry = json.loads(line)

    assert "\n" not in line
    assert entry["event"] == "readiness.check_failed"
    assert entry["level"] == "WARNING"
    assert entry["logger"] == "tessio.test"
    assert entry["dependency"] == "redis"
    assert datetime.fromisoformat(entry["timestamp"]).utcoffset() is not None
    assert "exception" not in entry
    assert "msg" not in entry
    assert "args" not in entry


def test_includes_the_exception_when_exc_info_is_set() -> None:
    entry = json.loads(JsonLogFormatter().format(build_record("job.failed", {}, is_failure=True)))

    assert "ValueError: boom" in entry["exception"]


def test_writes_non_json_values_as_text() -> None:
    entry = json.loads(JsonLogFormatter().format(build_record("job.done", {"value": Unserializable()})))

    assert entry["value"] == "unserializable value"


def test_leaves_out_the_uvicorn_color_message() -> None:
    record = build_record("Uvicorn running", {"color_message": "\u001b[1mUvicorn running\u001b[0m"})

    entry = json.loads(JsonLogFormatter().format(record))

    assert "color_message" not in entry
