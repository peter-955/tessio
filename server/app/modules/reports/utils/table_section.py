from app.modules.reports.domains.report_section.entity import ReportSection
from app.modules.reports.domains.report_table.entity import ReportTable
from app.modules.reports.typing.enums import ReportText
from app.modules.reports.utils.report_text import translate
from app.modules.users import UserLanguage


def build_table_section(
    heading: str, headers: list[str], rows: list[list[str]], language: UserLanguage
) -> ReportSection:
    return ReportSection(
        heading=heading,
        table=ReportTable(headers=headers, rows=rows) if rows else None,
        empty_text=None if rows else translate(language, ReportText.NOTHING_TO_SHOW),
    )
