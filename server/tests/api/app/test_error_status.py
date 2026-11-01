import pytest

from app.api.error_handlers import STATUS_BY_ERROR_CODE
from app.shared.typing.enums import ErrorCode


@pytest.mark.parametrize("error_code", list(ErrorCode))
def test_every_error_code_has_an_http_status(error_code: ErrorCode) -> None:
    assert error_code in STATUS_BY_ERROR_CODE
