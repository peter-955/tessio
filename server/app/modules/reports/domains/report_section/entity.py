from pydantic import Field

from app.modules.reports.domains.report_table.entity import ReportTable
from app.shared.common import Entity


class ReportSection(Entity):
    heading: str
    paragraphs: list[str] = Field(default_factory=list)
    table: ReportTable | None = None
    empty_text: str | None = None
