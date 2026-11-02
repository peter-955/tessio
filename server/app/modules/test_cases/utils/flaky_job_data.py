from uuid import UUID

from pydantic import JsonValue

from app.modules.test_cases.typing.constants.flaky_case import FLAKY_JOB_CASE_ID_KEY


def build_recompute_flaky_job_data(test_case_id: UUID) -> dict[str, JsonValue]:
    return {FLAKY_JOB_CASE_ID_KEY: str(test_case_id)}
