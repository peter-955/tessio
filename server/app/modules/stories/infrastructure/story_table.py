from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.stories.typing.enums import StorySource, TestStatus
from app.shared.postgres import TableBase, build_text_enum


class StoryTable(TableBase):
    __tablename__ = "stories"
    __table_args__ = (UniqueConstraint("project_id", "jira_id"), UniqueConstraint("project_id", "jira_key"))

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    sprint_id: Mapped[UUID | None] = mapped_column(ForeignKey("sprints.id"), index=True)
    jira_id: Mapped[str]
    jira_key: Mapped[str]
    jira_url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[JsonValue] = mapped_column(JSONB(none_as_null=True), nullable=True)
    jira_status: Mapped[str]
    jira_issue_type: Mapped[str]
    test_status: Mapped[TestStatus] = mapped_column(build_text_enum(TestStatus, "story_test_status"))
    test_status_changed_at: Mapped[datetime | None]
    test_status_changed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    jira_updated_at: Mapped[datetime]
    synced_at: Mapped[datetime]
    jira_missing_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
    source: Mapped[StorySource] = mapped_column(
        build_text_enum(StorySource, "story_source"), server_default=StorySource.JIRA.value
    )
