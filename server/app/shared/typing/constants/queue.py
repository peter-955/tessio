from datetime import timedelta

JOB_ATTEMPTS = 5
JOB_BACKOFF_DELAY = timedelta(seconds=30)
FAILED_JOB_RETENTION = timedelta(days=7)
