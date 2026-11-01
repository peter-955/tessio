from collections.abc import Mapping
from datetime import timedelta

MAX_SCREENSHOT_BYTES = 20971520
SCREENSHOT_UPLOAD_LIFETIME = timedelta(hours=1)
SCREENSHOT_CONTENT_TYPE_PREFIX = "image/"
PENDING_SCREENSHOT_CONTENT_TYPE = "image/jpeg"
PENDING_SCREENSHOT_SUFFIX = ".jpg"
SCREENSHOT_CONTENT_TYPE_BY_SUFFIX: Mapping[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".png": "image/png",
}
