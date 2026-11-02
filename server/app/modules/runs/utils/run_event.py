from uuid import UUID

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.run.entity import Run
from app.shared.events import LiveEvent, LiveEventType


def build_run_target_ids(run: Run) -> dict[str, str]:
    if run.test_suite_id is not None:
        return {"suiteId": str(run.test_suite_id)}
    if run.story_id is None:
        return {}
    return {"storyId": str(run.story_id)}


def build_run_started_event(run: Run, extra_ids: dict[str, str] | None = None) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_STARTED,
        project_id=run.project_id,
        ids={"runId": str(run.id), **build_run_target_ids(run), **(extra_ids or {})},
    )


def build_story_changed_event(run: Run, story_jira_key: str) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.STORY_CHANGED,
        project_id=run.project_id,
        ids={"storyId": str(run.story_id), "jiraKey": story_jira_key},
    )


def build_run_case_recorded_event(run: Run, case_result: CaseResult, case_story_id: UUID) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_CASE_RECORDED,
        project_id=run.project_id,
        ids={
            "runId": str(run.id),
            "caseResultId": str(case_result.id),
            "testCaseId": str(case_result.test_case_id),
            "storyId": str(case_story_id),
            **build_suite_ids(run),
        },
    )


def build_run_finished_event(run: Run) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_FINISHED,
        project_id=run.project_id,
        ids={"runId": str(run.id), **build_run_target_ids(run), "status": run.status.value},
    )


def build_suite_ids(run: Run) -> dict[str, str]:
    return {} if run.test_suite_id is None else {"suiteId": str(run.test_suite_id)}
