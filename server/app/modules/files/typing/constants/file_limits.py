from datetime import timedelta

MAX_FILE_BYTES = 20971520
MAX_AVATAR_BYTES = 2097152
UPLOAD_LIFETIME = timedelta(minutes=15)
DOWNLOAD_LINK_LIFETIME = timedelta(minutes=5)
ORPHAN_AGE = timedelta(days=1)
ORPHAN_BATCH_SIZE = 500
SCREENSHOT_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
AVATAR_CONTENT_TYPES = SCREENSHOT_CONTENT_TYPES
