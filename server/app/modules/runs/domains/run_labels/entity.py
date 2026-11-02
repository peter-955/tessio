from app.shared.common import Entity


class RunLabels(Entity):
    story_jira_key: str | None
    story_title: str | None
    environment_name: str
    environment_base_url: str
    started_by_name: str
    test_suite_name: str | None = None
