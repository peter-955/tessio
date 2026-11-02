from datetime import timedelta

FLAKY_RESULT_WINDOW = 10
FLAKY_FLIP_THRESHOLD = 3
QUARANTINE_RELEASE_PASS_COUNT = 10
DISAGREEMENT_WINDOW = timedelta(hours=24)
MAX_QUARANTINE_REASON_LENGTH = 500
FLAKY_JOB_CASE_ID_KEY = "testCaseId"
FLAKY_STATE_RESET: dict[str, object] = {"flaky_score": 0, "flaky_since": None, "disagreed_at": None}
