import json

import pytest
from fastapi import Request
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError

from app.api.error_handlers import handle_database_error
from app.shared.postgres import read_constraint_name, read_sqlstate


class DriverError(Exception):
    def __init__(self, sqlstate: str, constraint_name: str | None = None) -> None:
        super().__init__("driver error")
        self.sqlstate = sqlstate
        self.constraint_name = constraint_name


class AdaptedDriverError(Exception):
    def __init__(self, cause: DriverError) -> None:
        super().__init__("adapted error")
        self.sqlstate = cause.sqlstate
        self.__cause__ = cause


def build_request() -> Request:
    return Request({"type": "http", "method": "POST", "path": "/api/test", "headers": []})


def build_integrity_error(sqlstate: str, constraint_name: str | None = None) -> IntegrityError:
    return IntegrityError("INSERT", {}, AdaptedDriverError(DriverError(sqlstate, constraint_name)))


def test_the_sqlstate_and_constraint_are_read_from_the_driver_error() -> None:
    error = build_integrity_error("23505", "uq_example")

    assert read_sqlstate(error) == "23505"
    assert read_constraint_name(error) == "uq_example"


def test_an_error_without_driver_details_reads_as_none() -> None:
    error = DBAPIError("SELECT 1", {}, Exception("plain"))

    assert read_sqlstate(error) is None
    assert read_constraint_name(error) is None


async def test_a_unique_violation_becomes_a_conflict() -> None:
    response = await handle_database_error(build_request(), build_integrity_error("23505", "uq_example"))

    assert response.status_code == 409
    assert json.loads(bytes(response.body)) == {
        "code": "CONFLICT",
        "message": "This was changed at the same time by someone else. Reload and try again.",
    }


async def test_a_character_not_in_the_database_encoding_becomes_an_invalid_request() -> None:
    error = DBAPIError("SELECT", {}, AdaptedDriverError(DriverError("22021")))

    response = await handle_database_error(build_request(), error)

    assert response.status_code == 422
    assert json.loads(bytes(response.body))["code"] == "INVALID_REQUEST"


@pytest.mark.parametrize(
    "error",
    [
        build_integrity_error("23503", "fk_example"),
        OperationalError("SELECT", {}, AdaptedDriverError(DriverError("57P01"))),
    ],
)
async def test_other_database_errors_are_raised_again(error: DBAPIError) -> None:
    with pytest.raises(DBAPIError):
        await handle_database_error(build_request(), error)
