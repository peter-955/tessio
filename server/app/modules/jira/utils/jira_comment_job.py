from uuid import UUID

from pydantic import JsonValue

from app.modules.jira.domains.jira_comment_job.entity import JiraCommentJob
from app.modules.jira.typing.enums import JiraCommentTrigger


def build_jira_comment_job_data(job: JiraCommentJob) -> dict[str, JsonValue]:
    return {
        "trigger": job.trigger.value,
        "projectId": str(job.project_id),
        "storyId": str(job.story_id),
        "runId": None if job.run_id is None else str(job.run_id),
    }


def parse_jira_comment_job_data(data: dict[str, JsonValue]) -> JiraCommentJob | None:
    trigger = data.get("trigger")
    project_id = _parse_uuid(data.get("projectId"))
    story_id = _parse_uuid(data.get("storyId"))
    run_id = _parse_uuid(data.get("runId"))
    if not isinstance(trigger, str) or trigger not in set(JiraCommentTrigger) or project_id is None or story_id is None:
        return None
    return JiraCommentJob(trigger=JiraCommentTrigger(trigger), project_id=project_id, story_id=story_id, run_id=run_id)


def _parse_uuid(value: JsonValue) -> UUID | None:
    if not isinstance(value, str):
        return None
    try:
        return UUID(value)
    except ValueError:
        return None
