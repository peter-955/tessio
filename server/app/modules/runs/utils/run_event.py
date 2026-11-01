from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.run.entity import Run
from app.shared.events import LiveEvent, LiveEventType


def build_run_started_event(run: Run) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_STARTED,
        project_id=run.project_id,
        ids={"runId": str(run.id), "storyId": str(run.story_id)},
    )


def build_story_changed_event(run: Run, story_jira_key: str) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.STORY_CHANGED,
        project_id=run.project_id,
        ids={"storyId": str(run.story_id), "jiraKey": story_jira_key},
    )


def build_run_case_recorded_event(run: Run, case_result: CaseResult) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_CASE_RECORDED,
        project_id=run.project_id,
        ids={
            "runId": str(run.id),
            "caseResultId": str(case_result.id),
            "testCaseId": str(case_result.test_case_id),
            "storyId": str(run.story_id),
        },
    )


def build_run_finished_event(run: Run) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_FINISHED,
        project_id=run.project_id,
        ids={"runId": str(run.id), "storyId": str(run.story_id), "status": run.status.value},
    )
