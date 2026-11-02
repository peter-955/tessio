import re

from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_table.entity import ReportTable

MARKDOWN_SPECIAL_CHARACTERS = re.compile(r"([\\`*_{}\[\]<>|#])")


def escape_markdown(text: str) -> str:
    return MARKDOWN_SPECIAL_CHARACTERS.sub(r"\\\1", text)


def escape_cell(text: str) -> str:
    return " ".join(escape_markdown(text).split())


def render_markdown_table(table: ReportTable) -> list[str]:
    return [
        "| " + " | ".join(escape_cell(header) for header in table.headers) + " |",
        "| " + " | ".join("---" for _ in table.headers) + " |",
        *("| " + " | ".join(escape_cell(cell) for cell in row) + " |" for row in table.rows),
    ]


def render_markdown(document: ReportDocument) -> str:
    blocks = [
        f"# {escape_markdown(document.title)}",
        escape_markdown(document.subtitle),
        "\n".join(f"- **{escape_markdown(fact.label)}:** {escape_cell(fact.value)}" for fact in document.facts),
    ]
    for section in document.sections:
        blocks.append(f"## {escape_markdown(section.heading)}")
        blocks.extend(escape_markdown(paragraph) for paragraph in section.paragraphs)
        if section.table is not None:
            blocks.append("\n".join(render_markdown_table(section.table)))
        elif section.empty_text is not None:
            blocks.append(f"_{escape_markdown(section.empty_text)}_")
    return "\n\n".join(block for block in blocks if block) + "\n"
