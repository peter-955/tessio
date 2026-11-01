from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.shared.typing.enums import ErrorCode

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
SAME_SITE_FETCH_VALUES = {"same-origin", "none"}


class OriginCheckMiddleware:
    def __init__(self, app: ASGIApp, allowed_origins: set[str]) -> None:
        self._app = app
        self._allowed_origins = allowed_origins

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self._is_checked_request(scope) and not self._is_allowed(Headers(scope=scope)):
            response = JSONResponse(
                status_code=403,
                content={
                    "code": ErrorCode.ORIGIN_NOT_ALLOWED.value,
                    "message": "This request comes from another site.",
                },
            )
            await response(scope, receive, send)
            return
        await self._app(scope, receive, send)

    def _is_checked_request(self, scope: Scope) -> bool:
        return scope["type"] == "http" and scope["method"] not in SAFE_METHODS and scope["path"].startswith("/api/")

    def _is_allowed(self, headers: Headers) -> bool:
        origin = headers.get("origin")
        if origin is not None:
            return origin in self._allowed_origins
        fetch_site = headers.get("sec-fetch-site")
        return fetch_site is None or fetch_site in SAME_SITE_FETCH_VALUES
