from datetime import datetime

from app.shared.common import Entity


class DownloadLink(Entity):
    url: str
    expires_at: datetime
