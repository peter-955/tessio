from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.api.error_response import ErrorResponse
from app.shared.common import TessioError
from app.shared.postgres import CHARACTER_NOT_IN_REPERTOIRE_SQLSTATE, UNIQUE_VIOLATION_SQLSTATE, read_sqlstate
from app.shared.rate_limit import RateLimitedError
from app.shared.typing.enums import ErrorCode

CONCURRENT_CHANGE_MESSAGE = "This was changed at the same time by someone else. Reload and try again."
DISALLOWED_CHARACTERS_MESSAGE = "The request contains characters that are not allowed."

STATUS_BY_ERROR_CODE = {
    ErrorCode.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.INVALID_ONE_TIME_LINK: status.HTTP_400_BAD_REQUEST,
    ErrorCode.WEAK_PASSWORD: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.PASSWORD_BREACHED: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.SIGN_IN_LOCKED: status.HTTP_429_TOO_MANY_REQUESTS,
    ErrorCode.ORIGIN_NOT_ALLOWED: status.HTTP_403_FORBIDDEN,
    ErrorCode.EMAIL_ALREADY_USED: status.HTTP_409_CONFLICT,
    ErrorCode.NOT_SIGNED_IN: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
    ErrorCode.INVALID_TWO_FACTOR_CODE: status.HTTP_400_BAD_REQUEST,
    ErrorCode.TWO_FACTOR_ALREADY_SET_UP: status.HTTP_409_CONFLICT,
    ErrorCode.TWO_FACTOR_SETUP_NOT_STARTED: status.HTTP_409_CONFLICT,
    ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
    ErrorCode.INVALID_REQUEST: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.PROJECT_ARCHIVED: status.HTTP_409_CONFLICT,
    ErrorCode.PROJECT_KEY_ALREADY_USED: status.HTTP_409_CONFLICT,
    ErrorCode.LAST_PROJECT_ADMIN: status.HTTP_409_CONFLICT,
    ErrorCode.JIRA_NOT_CONFIGURED: status.HTTP_409_CONFLICT,
    ErrorCode.JIRA_UNREACHABLE: status.HTTP_502_BAD_GATEWAY,
    ErrorCode.JIRA_INVALID_CREDENTIALS: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.JIRA_PROJECT_ALREADY_LINKED: status.HTTP_409_CONFLICT,
    ErrorCode.INVALID_API_TOKEN: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.TOKEN_LIMIT_REACHED: status.HTTP_409_CONFLICT,
    ErrorCode.OWNER_ONLY: status.HTTP_403_FORBIDDEN,
    ErrorCode.CANNOT_CHANGE_OWN_OR_OWNER: status.HTTP_409_CONFLICT,
    ErrorCode.USER_DEACTIVATED: status.HTTP_409_CONFLICT,
    ErrorCode.USER_NOT_INVITED: status.HTTP_409_CONFLICT,
    ErrorCode.INVALID_CURRENT_PASSWORD: status.HTTP_400_BAD_REQUEST,
    ErrorCode.FILE_TYPE_NOT_ALLOWED: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.FILE_TOO_LARGE: status.HTTP_413_CONTENT_TOO_LARGE,
    ErrorCode.UPLOAD_NOT_COMPLETED: status.HTTP_409_CONFLICT,
    ErrorCode.IMPORT_INVALID_FILE: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.ENVIRONMENT_NAME_ALREADY_USED: status.HTTP_409_CONFLICT,
    ErrorCode.ENVIRONMENT_IN_USE: status.HTTP_409_CONFLICT,
    ErrorCode.TEST_DATA_KEY_ALREADY_USED: status.HTTP_409_CONFLICT,
    ErrorCode.INVALID_STATUS_TRANSITION: status.HTTP_409_CONFLICT,
    ErrorCode.STORY_SIGN_OFF_BLOCKED: status.HTTP_409_CONFLICT,
    ErrorCode.CASE_NOT_READY: status.HTTP_409_CONFLICT,
    ErrorCode.UNKNOWN_REFERENCE: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.GAP_NOT_OPEN: status.HTTP_409_CONFLICT,
    ErrorCode.ASSIGNEE_NOT_ACTIVE_MEMBER: status.HTTP_409_CONFLICT,
    ErrorCode.OPEN_GAPS_BLOCK_RUN: status.HTTP_409_CONFLICT,
    ErrorCode.NO_READY_CASES: status.HTTP_409_CONFLICT,
    ErrorCode.RUN_ALREADY_RUNNING: status.HTTP_409_CONFLICT,
    ErrorCode.RUN_NOT_RUNNING: status.HTTP_409_CONFLICT,
    ErrorCode.RUN_NOT_OWNED: status.HTTP_403_FORBIDDEN,
    ErrorCode.RUN_NOT_FINISHED: status.HTTP_409_CONFLICT,
    ErrorCode.NO_FAILED_CASES_TO_RERUN: status.HTTP_409_CONFLICT,
    ErrorCode.CASE_RESULT_EXISTS: status.HTTP_409_CONFLICT,
    ErrorCode.RUN_NOT_MANUAL: status.HTTP_409_CONFLICT,
    ErrorCode.RATE_LIMITED: status.HTTP_429_TOO_MANY_REQUESTS,
}


async def handle_tessio_error(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, TessioError):
        raise error
    headers = {"Retry-After": str(error.retry_after_seconds)} if isinstance(error, RateLimitedError) else None
    return build_error_response(STATUS_BY_ERROR_CODE[error.code], error.code, error.message, headers)


async def handle_database_error(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, DBAPIError):
        raise error
    sqlstate = read_sqlstate(error)
    if isinstance(error, IntegrityError) and sqlstate == UNIQUE_VIOLATION_SQLSTATE:
        return build_error_response(status.HTTP_409_CONFLICT, ErrorCode.CONFLICT, CONCURRENT_CHANGE_MESSAGE)
    if sqlstate == CHARACTER_NOT_IN_REPERTOIRE_SQLSTATE:
        return build_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT, ErrorCode.INVALID_REQUEST, DISALLOWED_CHARACTERS_MESSAGE
        )
    raise error


def build_error_response(
    status_code: int, code: ErrorCode, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(code=code, message=message).model_dump(mode="json", by_alias=True),
        headers=headers,
    )


def register_error_handlers(application: FastAPI) -> None:
    application.add_exception_handler(TessioError, handle_tessio_error)
    application.add_exception_handler(DBAPIError, handle_database_error)
