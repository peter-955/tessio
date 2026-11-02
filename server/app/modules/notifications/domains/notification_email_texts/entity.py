from collections.abc import Mapping

from app.modules.notifications.typing.enums import RunOutcome
from app.shared.common import Entity


class NotificationEmailTexts(Entity):
    greeting: str
    project_line: str
    open_line: str
    footer: str
    gap_assigned_title: str
    failure_assigned_title: str
    run_finished_titles: Mapping[RunOutcome, str]
    suite_run_finished_titles: Mapping[RunOutcome, str]
    run_counts: str
    report_ready_title: str
