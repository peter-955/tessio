from datetime import timedelta

HALF_SESSION_LIFETIME = timedelta(minutes=10)
SESSION_IDLE_LIFETIME = timedelta(days=7)
LAST_SEEN_REFRESH_INTERVAL = timedelta(minutes=1)
INVITE_LIFETIME = timedelta(days=7)
PASSWORD_RESET_LIFETIME = timedelta(minutes=30)
MAXIMUM_FAILED_SIGN_INS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
DUMMY_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$jBRu0kIqweNzsvgSoFTJAQ$fOaM96B6YLP8htaQ8ibA3l/UxfgtTFcXq5OKrmECGYc"  # noqa: S105
)
MINIMUM_PASSWORD_LENGTH = 12
RECOVERY_CODE_COUNT = 10
TOTP_ISSUER = "Tessio"
