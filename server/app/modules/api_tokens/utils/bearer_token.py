from app.modules.api_tokens.typing.constants import BEARER_SCHEME


def read_bearer_token(authorization: str) -> str | None:
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != BEARER_SCHEME or not value:
        return None
    return value
