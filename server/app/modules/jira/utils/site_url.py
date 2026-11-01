import re
from urllib.parse import urlsplit

from app.modules.jira.errors import InvalidJiraSiteUrlError
from app.modules.jira.typing.constants import JIRA_DEFAULT_PORT_BY_SCHEME, JIRA_SITE_HOST_PATTERN


def normalize_site_url(site_url: str) -> str:
    try:
        parts = urlsplit(site_url.strip())
        port = parts.port
    except ValueError as error:
        raise InvalidJiraSiteUrlError from error
    scheme = parts.scheme.lower()
    host = parts.hostname or ""
    if parts.username is not None or parts.password is not None:
        raise InvalidJiraSiteUrlError
    if re.fullmatch(JIRA_SITE_HOST_PATTERN, host) is None:
        raise InvalidJiraSiteUrlError
    if scheme != "https" and not (scheme == "http" and "." not in host):
        raise InvalidJiraSiteUrlError
    if port is None or port == JIRA_DEFAULT_PORT_BY_SCHEME[scheme]:
        return f"{scheme}://{host}"
    return f"{scheme}://{host}:{port}"
