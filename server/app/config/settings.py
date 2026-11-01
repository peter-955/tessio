from functools import lru_cache

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.mailer import SmtpSecurity

ENVIRONMENT_FILE = SettingsConfigDict(env_file=".env", extra="ignore")


class DatabaseSettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    database_url: str = Field(validation_alias="DATABASE_URL")


class MailSettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    smtp_host: str = Field(default="localhost", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=3206, validation_alias="SMTP_PORT")
    mail_sender: str = Field(default="Tessio <no-reply@tessio.local>", validation_alias="MAIL_SENDER")
    smtp_username: str | None = Field(default=None, validation_alias="SMTP_USERNAME")
    smtp_password: SecretStr | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_security: SmtpSecurity = Field(default=SmtpSecurity.NONE, validation_alias="SMTP_SECURITY")


class QueueSettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    redis_url: str = Field(default="redis://localhost:3204", validation_alias="REDIS_URL")


class SecuritySettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    encryption_key: SecretStr = Field(validation_alias="TESSIO_ENCRYPTION_KEY")
    encryption_key_id: int = Field(default=1, ge=0, le=255, validation_alias="TESSIO_ENCRYPTION_KEY_ID")
    previous_encryption_keys: SecretStr | None = Field(default=None, validation_alias="TESSIO_PREVIOUS_ENCRYPTION_KEYS")
    is_session_cookie_secure: bool = Field(default=True, validation_alias="SESSION_COOKIE_SECURE")


class StorageSettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    s3_endpoint_url: str | None = Field(default=None, validation_alias="S3_ENDPOINT_URL")
    s3_public_endpoint_url: str | None = Field(default=None, validation_alias="S3_PUBLIC_ENDPOINT_URL")
    s3_region: str = Field(default="eu-west-3", validation_alias="S3_REGION")
    s3_bucket: str = Field(validation_alias="S3_BUCKET")
    s3_access_key_id: SecretStr | None = Field(default=None, validation_alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: SecretStr | None = Field(default=None, validation_alias="S3_SECRET_ACCESS_KEY")


class ClientSettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    client_url: str = Field(default="http://localhost:3201", validation_alias="CLIENT_URL")


class ObservabilitySettings(BaseSettings):
    model_config = ENVIRONMENT_FILE

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    sentry_dsn: str | None = Field(default=None, validation_alias="SENTRY_DSN")
    sentry_environment: str = Field(default="development", validation_alias="SENTRY_ENVIRONMENT")


class Settings(BaseModel):
    database: DatabaseSettings
    mail: MailSettings
    queue: QueueSettings
    security: SecuritySettings
    storage: StorageSettings
    client: ClientSettings
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database=DatabaseSettings(),
        mail=MailSettings(),
        queue=QueueSettings(),
        security=SecuritySettings(),
        storage=StorageSettings(),
        client=ClientSettings(),
        observability=ObservabilitySettings(),
    )
