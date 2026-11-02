from uuid import UUID

from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.errors import RunCaseNotFoundError


def resolve_case_story_id(run: Run, run_case: RunCaseView) -> UUID:
    story_id = run_case.story_id or run.story_id
    if story_id is None:
        raise RunCaseNotFoundError
    return story_id
