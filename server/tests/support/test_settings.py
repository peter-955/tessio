import base64
import os

from app.config import (
    ClientSettings,
    DatabaseSettings,
    MailSettings,
    QueueSettings,
    SecuritySettings,
    Settings,
    StorageSettings,
)


def build_test_settings(database_url: str, redis_url: str | None = None) -> Settings:
    return Settings(
        database=DatabaseSettings.model_validate({"DATABASE_URL": database_url}),
        mail=MailSettings(),
        queue=QueueSettings() if redis_url is None else QueueSettings.model_validate({"REDIS_URL": redis_url}),
        security=SecuritySettings.model_validate(
            {"TESSIO_ENCRYPTION_KEY": base64.b64encode(os.urandom(32)).decode(), "SESSION_COOKIE_SECURE": True}
        ),
        storage=StorageSettings.model_validate({"S3_BUCKET": "tessio"}),
        client=ClientSettings.model_validate({"CLIENT_URL": "https://tessio.test"}),
    )
