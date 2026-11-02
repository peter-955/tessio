import logging
import sys

import sentry_sdk
from sentry_sdk.integrations.httpx import HttpxIntegration

from app.shared.logging.json_log_formatter import JsonLogFormatter
from app.shared.logging.typing.constants.http_client import HTTP_CLIENT_LOGGER_LEVEL, HTTP_CLIENT_LOGGER_NAMES
from app.shared.logging.typing.constants.uvicorn import UVICORN_LOGGER_NAMES


def configure_logging(level: str, sentry_dsn: str | None, environment: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level.upper())
    for logger_name in UVICORN_LOGGER_NAMES:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
    for logger_name in HTTP_CLIENT_LOGGER_NAMES:
        logging.getLogger(logger_name).setLevel(HTTP_CLIENT_LOGGER_LEVEL)
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            send_default_pii=False,
            traces_sample_rate=0.0,
            max_request_body_size="never",
            include_local_variables=False,
            disabled_integrations=[HttpxIntegration()],
        )
