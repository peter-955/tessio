import json
import logging
from datetime import UTC, datetime

from app.shared.logging.typing.constants.log_record import (
    OMITTED_LOG_RECORD_ATTRIBUTES,
    STANDARD_LOG_RECORD_ATTRIBUTES,
)


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key in STANDARD_LOG_RECORD_ATTRIBUTES or key in OMITTED_LOG_RECORD_ATTRIBUTES or key in entry:
                continue
            entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)
