from datetime import datetime

from pydantic import BaseModel, ConfigDict, JsonValue
from pydantic.alias_generators import to_camel

from app.modules.jira.typing.enums import JiraSprintState


class JiraPayload(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, validate_by_name=True, extra="ignore")


class JiraMyselfPayload(JiraPayload):
    account_id: str
    display_name: str
    email_address: str | None = None


class JiraProjectPayload(JiraPayload):
    id: str
    key: str
    name: str


class JiraProjectPagePayload(JiraPayload):
    values: list[JiraProjectPayload]
    is_last: bool = True


class JiraBoardPayload(JiraPayload):
    id: int
    name: str
    type: str


class JiraBoardPagePayload(JiraPayload):
    values: list[JiraBoardPayload]
    is_last: bool = True


class JiraSprintPayload(JiraPayload):
    id: int
    name: str
    state: JiraSprintState
    start_date: datetime | None = None
    end_date: datetime | None = None
    complete_date: datetime | None = None


class JiraSprintPagePayload(JiraPayload):
    values: list[JiraSprintPayload]
    is_last: bool = True


class JiraNamedPayload(JiraPayload):
    name: str


class JiraIssueTypePayload(JiraPayload):
    name: str
    subtask: bool = False


class JiraIssueFieldsPayload(JiraPayload):
    summary: str
    description: JsonValue = None
    status: JiraNamedPayload
    issuetype: JiraIssueTypePayload
    updated: datetime


class JiraIssuePayload(JiraPayload):
    id: str
    key: str
    fields: JiraIssueFieldsPayload


class JiraIssueSearchPagePayload(JiraPayload):
    issues: list[JiraIssuePayload]
    next_page_token: str | None = None
    is_last: bool | None = None


class JiraCreatedIssuePayload(JiraPayload):
    id: str
    key: str


class JiraStatusCategoryPayload(JiraPayload):
    key: str


class JiraStatusPayload(JiraPayload):
    name: str
    status_category: JiraStatusCategoryPayload


class JiraStatusFieldsPayload(JiraPayload):
    status: JiraStatusPayload


class JiraIssueStatusPayload(JiraPayload):
    key: str
    fields: JiraStatusFieldsPayload


class JiraIssueStatusPagePayload(JiraPayload):
    issues: list[JiraIssueStatusPayload]
    next_page_token: str | None = None
    is_last: bool | None = None


class JiraPermissionPayload(JiraPayload):
    have_permission: bool = False


class JiraMyPermissionsPayload(JiraPayload):
    permissions: dict[str, JiraPermissionPayload]
