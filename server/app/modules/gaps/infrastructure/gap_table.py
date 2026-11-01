from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.gaps.typing.enums import GapDataScope, GapSeverity, GapStatus, GapTargetType, GapType
from app.shared.permissions import ProjectRole
from app.shared.postgres import TableBase, build_text_enum


class GapTable(TableBase):
    __tablename__ = "gaps"
    __table_args__ = (Index("ix_gaps_story_id_status", "story_id", "status"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    story_id: Mapped[UUID] = mapped_column(ForeignKey("stories.id"))
    target_type: Mapped[GapTargetType] = mapped_column(build_text_enum(GapTargetType, "gap_target_type"))
    target_id: Mapped[UUID | None]
    type: Mapped[GapType] = mapped_column(build_text_enum(GapType, "gap_type"))
    data_scope: Mapped[GapDataScope | None] = mapped_column(build_text_enum(GapDataScope, "gap_data_scope"))
    severity: Mapped[GapSeverity] = mapped_column(build_text_enum(GapSeverity, "gap_severity"))
    question: Mapped[str] = mapped_column(Text)
    status: Mapped[GapStatus] = mapped_column(build_text_enum(GapStatus, "gap_status"))
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    assignee_role: Mapped[ProjectRole | None] = mapped_column(build_text_enum(ProjectRole, "gap_assignee_role"))
    raised_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    raised_via_token_id: Mapped[UUID | None] = mapped_column(Uuid)
    answer: Mapped[str | None] = mapped_column(Text)
    answered_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    answered_at: Mapped[datetime | None]
    reopened_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    reopened_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
