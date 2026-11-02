from uuid import UUID

from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.typing.enums import RunStatus


def list_jira_comment_story_ids(run: Run, report: RunReport | None) -> list[UUID]:
    if run.status is RunStatus.ABORTED:
        return []
    if run.story_id is not None:
        return [run.story_id]
    if report is None:
        return []
    return list(dict.fromkeys(story.story_id for story in report.stories))
