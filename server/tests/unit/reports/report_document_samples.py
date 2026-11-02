from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_fact.entity import ReportFact
from app.modules.reports.domains.report_section.entity import ReportSection
from app.modules.reports.domains.report_table.entity import ReportTable


def build_sample_document(hidden_value: str = "s3cr3t") -> ReportDocument:
    return ReportDocument(
        title="Run report · SHOP-1 Pay | refund",
        subtitle="0190f3b6",
        facts=[ReportFact(label="Status", value="Failed"), ReportFact(label="Environment", value="Staging")],
        sections=[
            ReportSection(heading="Summary", paragraphs=[f"Token {hidden_value} leaked <script>"]),
            ReportSection(
                heading="Cases",
                table=ReportTable(
                    headers=["Case", "Actual result"],
                    rows=[["TC-1", f"Typed {hidden_value}\nthen saw *500*"], ["TC-2", "Thành công · réussi"]],
                ),
            ),
            ReportSection(heading="Open gaps", empty_text="Nothing to show."),
        ],
    )
