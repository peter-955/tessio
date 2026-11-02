from app.modules.reports.domains.report_fact.entity import ReportFact
from app.modules.reports.domains.report_section.entity import ReportSection
from app.shared.common import Entity


class ReportDocument(Entity):
    title: str
    subtitle: str
    facts: list[ReportFact]
    sections: list[ReportSection]
