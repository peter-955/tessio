import logging

STANDARD_LOG_RECORD_ATTRIBUTES: frozenset[str] = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", None, None)).keys() | {"message", "asctime", "taskName"}
)
OMITTED_LOG_RECORD_ATTRIBUTES: frozenset[str] = frozenset({"color_message"})
