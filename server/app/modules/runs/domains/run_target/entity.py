from app.shared.common import Entity


class RunTarget(Entity):
    story_jira_key: str | None
    suite_name: str | None
