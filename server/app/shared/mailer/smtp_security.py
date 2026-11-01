from enum import StrEnum


class SmtpSecurity(StrEnum):
    NONE = "none"
    STARTTLS = "starttls"
    TLS = "tls"
