from typing import Annotated, Literal
from uuid import UUID

from pydantic import BeforeValidator, Field

from app.modules.notifications.typing.enums import NotificationKind, ReportFormat, ReportSource, RunOutcome
from app.modules.notifications.utils.shorten_text import shorten_text
from app.shared.common import Entity

ShortText = Annotated[str, BeforeValidator(shorten_text)]


class GapAssignedPayload(Entity):
    kind: Literal[NotificationKind.GAP_ASSIGNED] = NotificationKind.GAP_ASSIGNED
    gap_id: UUID
    story_id: UUID
    story_jira_key: str
    question: ShortText


class FailureAssignedPayload(Entity):
    kind: Literal[NotificationKind.FAILURE_ASSIGNED] = NotificationKind.FAILURE_ASSIGNED
    failure_id: UUID
    test_case_id: UUID
    test_case_code: str
    test_case_title: ShortText
    story_jira_key: str


class RunFinishedPayload(Entity):
    kind: Literal[NotificationKind.RUN_FINISHED] = NotificationKind.RUN_FINISHED
    run_id: UUID
    story_id: UUID
    story_jira_key: str
    outcome: RunOutcome
    passed_count: int
    failed_count: int
    blocked_count: int


class SuiteRunFinishedPayload(Entity):
    kind: Literal[NotificationKind.SUITE_RUN_FINISHED] = NotificationKind.SUITE_RUN_FINISHED
    run_id: UUID
    test_suite_id: UUID
    test_suite_name: ShortText
    outcome: RunOutcome
    passed_count: int
    failed_count: int
    blocked_count: int


class ReportReadyPayload(Entity):
    kind: Literal[NotificationKind.REPORT_READY] = NotificationKind.REPORT_READY
    file_id: UUID
    file_name: ShortText
    format: ReportFormat
    source: ReportSource
    source_id: str
    source_label: ShortText


NotificationPayload = Annotated[
    GapAssignedPayload | FailureAssignedPayload | RunFinishedPayload | SuiteRunFinishedPayload | ReportReadyPayload,
    Field(discriminator="kind"),
]
