from enum import StrEnum


class AuditAction(StrEnum):
    SECRET_REVEAL = "secret.reveal"
    SECRET_RESOLVE = "secret.resolve"
