from datetime import timedelta

from app.shared.rate_limit import RateLimitRule

SIGN_IN_RATE_LIMIT = RateLimitRule(name="sign_in", limit=20, window=timedelta(minutes=15))
TWO_FACTOR_RATE_LIMIT = RateLimitRule(name="two_factor", limit=20, window=timedelta(minutes=15))
ONE_TIME_LINK_RATE_LIMIT = RateLimitRule(name="one_time_link", limit=20, window=timedelta(minutes=15))
PASSWORD_FORGOT_RATE_LIMIT = RateLimitRule(name="password_forgot", limit=10, window=timedelta(hours=1))
PASSWORD_FORGOT_EMAIL_RATE_LIMIT = RateLimitRule(name="password_forgot_email", limit=3, window=timedelta(hours=1))
UNKNOWN_CLIENT_HOST = "unknown"
