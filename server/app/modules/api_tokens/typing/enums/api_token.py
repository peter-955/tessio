from enum import StrEnum


class ApiTokenStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ApiTokenScope(StrEnum):
    MCP = "mcp"
    API = "api"
