from sqlalchemy.exc import DBAPIError


def read_sqlstate(error: DBAPIError) -> str | None:
    return _read_text_attribute(error, "sqlstate")


def read_constraint_name(error: DBAPIError) -> str | None:
    return _read_text_attribute(error, "constraint_name")


def _read_text_attribute(error: DBAPIError, attribute_name: str) -> str | None:
    for source in (error.orig, getattr(error.orig, "__cause__", None)):
        value = getattr(source, attribute_name, None)
        if isinstance(value, str):
            return value
    return None
