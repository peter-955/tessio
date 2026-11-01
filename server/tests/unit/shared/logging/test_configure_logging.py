import logging
from collections.abc import Iterator

import pytest
import sentry_sdk

from app.shared.logging import JsonLogFormatter, configure_logging


@pytest.fixture(autouse=True)
def restore_root_logger() -> Iterator[None]:
    root_logger = logging.getLogger()
    handlers = list(root_logger.handlers)
    level = root_logger.level
    yield
    root_logger.handlers.clear()
    root_logger.handlers.extend(handlers)
    root_logger.setLevel(level)


@pytest.fixture
def sentry_calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []

    def record_init(**options: object) -> None:
        calls.append(options)

    monkeypatch.setattr(sentry_sdk, "init", record_init)
    return calls


def test_root_logger_has_one_json_handler(sentry_calls: list[dict[str, object]]) -> None:
    configure_logging("debug", None, "test")
    configure_logging("info", None, "test")

    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0].formatter, JsonLogFormatter)
    assert root_logger.level == logging.INFO


def test_uvicorn_loggers_propagate_to_the_root(sentry_calls: list[dict[str, object]]) -> None:
    logging.getLogger("uvicorn.access").addHandler(logging.NullHandler())

    configure_logging("INFO", None, "test")

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        assert uvicorn_logger.handlers == []
        assert uvicorn_logger.propagate


@pytest.mark.parametrize("sentry_dsn", [None, ""])
def test_sentry_is_not_initialised_without_a_dsn(sentry_calls: list[dict[str, object]], sentry_dsn: str | None) -> None:
    configure_logging("INFO", sentry_dsn, "test")

    assert sentry_calls == []


def test_sentry_is_initialised_with_a_dsn(sentry_calls: list[dict[str, object]]) -> None:
    configure_logging("INFO", "https://key@sentry.test/1", "production")

    assert sentry_calls == [
        {
            "dsn": "https://key@sentry.test/1",
            "environment": "production",
            "send_default_pii": False,
            "traces_sample_rate": 0.0,
            "max_request_body_size": "never",
            "include_local_variables": False,
        }
    ]


def test_sentry_never_receives_request_bodies_or_stack_locals(sentry_calls: list[dict[str, object]]) -> None:
    configure_logging("INFO", "https://key@sentry.test/1", "production")

    assert sentry_calls[0]["max_request_body_size"] == "never"
    assert sentry_calls[0]["include_local_variables"] is False
    assert sentry_calls[0]["send_default_pii"] is False
