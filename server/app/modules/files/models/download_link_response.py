from datetime import datetime

from app.shared.common import WireModel


class DownloadLinkResponse(WireModel):
    url: str
    expires_at: datetime
