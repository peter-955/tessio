from enum import StrEnum


class ProjectRole(StrEnum):
    ADMIN = "admin"
    PM = "pm"
    BA = "ba"
    QC = "qc"
    DEV = "dev"
    VIEWER = "viewer"
