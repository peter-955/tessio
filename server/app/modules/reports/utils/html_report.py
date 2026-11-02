from html import escape

from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_table.entity import ReportTable
from app.modules.reports.typing.constants import REPORT_STYLE
from app.modules.users import UserLanguage


def render_html_table(table: ReportTable) -> str:
    header = "".join(f"<th>{escape(header)}</th>" for header in table.headers)
    rows = "".join("<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>" for row in table.rows)
    return f"<table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>"


def render_html(document: ReportDocument, language: UserLanguage) -> str:
    facts = "".join(f"<dt>{escape(fact.label)}</dt><dd>{escape(fact.value)}</dd>" for fact in document.facts)
    sections: list[str] = []
    for section in document.sections:
        parts = [f"<h2>{escape(section.heading)}</h2>"]
        parts.extend(f"<p>{escape(paragraph)}</p>" for paragraph in section.paragraphs)
        if section.table is not None:
            parts.append(render_html_table(section.table))
        elif section.empty_text is not None:
            parts.append(f'<p class="empty">{escape(section.empty_text)}</p>')
        sections.append("<section>" + "".join(parts) + "</section>")
    return (
        f'<!doctype html><html lang="{escape(language.value)}"><head><meta charset="utf-8">'
        f"<title>{escape(document.title)}</title><style>{REPORT_STYLE}</style></head><body>"
        f'<h1>{escape(document.title)}</h1><p class="subtitle">{escape(document.subtitle)}</p>'
        f'<dl class="facts">{facts}</dl>{"".join(sections)}</body></html>'
    )
