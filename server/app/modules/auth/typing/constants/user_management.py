from datetime import timedelta

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
MAX_USER_NAME_LENGTH = 100
MAX_USER_QUERY_LENGTH = 100
AVATAR_LINK_LIFETIME = timedelta(minutes=5)
AVATAR_CACHE_CONTROL = "private, max-age=240"
