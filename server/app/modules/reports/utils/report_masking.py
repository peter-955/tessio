from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_fact.entity import ReportFact
from app.modules.reports.domains.report_section.entity import ReportSection
from app.modules.reports.domains.report_table.entity import ReportTable
from app.shared.masking import SecretMasker


def mask_table(table: ReportTable | None, masker: SecretMasker) -> ReportTable | None:
    if table is None:
        return None
    return ReportTable(
        headers=[masker.mask(header) for header in table.headers],
        rows=[[masker.mask(cell) for cell in row] for row in table.rows],
    )


def mask_document(document: ReportDocument, masker: SecretMasker) -> ReportDocument:
    return ReportDocument(
        title=masker.mask(document.title),
        subtitle=masker.mask(document.subtitle),
        facts=[ReportFact(label=fact.label, value=masker.mask(fact.value)) for fact in document.facts],
        sections=[
            ReportSection(
                heading=section.heading,
                paragraphs=[masker.mask(paragraph) for paragraph in section.paragraphs],
                table=mask_table(section.table, masker),
                empty_text=section.empty_text,
            )
            for section in document.sections
        ],
    )
