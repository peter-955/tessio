from app.modules.story_context.domains.run_scope.entity import RunScope
from app.modules.story_context.errors import RunNotFoundError, RunNotOwnedError, RunNotRunningError
from app.shared.permissions import Actor


def ensure_own_running_run(run: RunScope | None, actor: Actor) -> RunScope:
    if run is None:
        raise RunNotFoundError
    if run.started_by != actor.user_id:
        raise RunNotOwnedError
    if not run.is_running:
        raise RunNotRunningError
    return run
