from enum import StrEnum


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class UserStatus(StrEnum):
    INVITED = "invited"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class UserLanguage(StrEnum):
    EN = "en"
    FR = "fr"
    VI = "vi"


class ColorScheme(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
