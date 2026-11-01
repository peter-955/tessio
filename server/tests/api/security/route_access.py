from enum import StrEnum


class RouteAccess(StrEnum):
    PUBLIC = "public"
    SESSION = "session"
    WORKSPACE = "workspace"
    PROJECT_READ = "project_read"
    PROJECT_WRITE = "project_write"
    API_TOKEN = "api_token"
