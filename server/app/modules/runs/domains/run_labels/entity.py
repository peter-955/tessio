from app.shared.common import Entity


class RunLabels(Entity):
    story_jira_key: str
    story_title: str
    environment_name: str
    started_by_name: str
