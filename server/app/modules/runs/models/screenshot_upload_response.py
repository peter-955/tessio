from app.shared.common import WireModel


class ScreenshotUploadResponse(WireModel):
    url: str
    fields: dict[str, str]
    key_prefix: str
