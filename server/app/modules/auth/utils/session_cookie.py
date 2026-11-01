from fastapi import Response

from app.modules.auth.typing.constants.session_cookie import SESSION_COOKIE_LIFETIME, SESSION_COOKIE_NAME


def set_session_cookie(response: Response, token: str, is_secure: bool) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=int(SESSION_COOKIE_LIFETIME.total_seconds()),
        httponly=True,
        secure=is_secure,
        samesite="lax",
    )


def clear_session_cookie(response: Response, is_secure: bool) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, httponly=True, secure=is_secure, samesite="lax")
