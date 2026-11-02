from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, LargeBinary, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class JiraConnectionTable(TableBase):
    __tablename__ = "jira_connection"
    __table_args__ = (CheckConstraint("id = 1", name="ck_jira_connection_singleton"),)

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    site_url: Mapped[str] = mapped_column(Text)
    account_email: Mapped[str] = mapped_column(Text)
    api_token_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    account_id: Mapped[str] = mapped_column(Text)
    account_display_name: Mapped[str] = mapped_column(Text)
    configured_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    configured_at: Mapped[datetime]
    can_create_issues: Mapped[bool | None]
    can_comment: Mapped[bool | None]
    missing_permissions: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default=text("'{}'"))
    permissions_checked_at: Mapped[datetime | None]
