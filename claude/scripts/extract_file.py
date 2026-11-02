#!/usr/bin/env python3
"""Print the text of an .xlsx or .docx file so Claude can read it.

Usage: python3 extract_file.py <file>

.xlsx: one block per sheet, each non-empty row as `row <n>: cell | cell | ...`, merged cells repeated.
.docx: paragraphs and tables in document order.
Inside a cell, a line break is shown as ⏎ and a | as \\|.
Only the standard library is used, so python3 3.9 or later is enough.
"""

from __future__ import annotations

import posixpath
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple
from xml.etree import ElementTree

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_UNPACKED_BYTES = 100 * 1024 * 1024
MAX_ROWS = 5000
LINE_BREAK_MARK = " ⏎ "
CELL_SEPARATOR = " | "
CELL_REFERENCE = re.compile(r"^([A-Z]+)(\d+)$")
OFFICE_RELATIONSHIP_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
STRICT_RELATIONSHIP_ID = "{http://purl.oclc.org/ooxml/officeDocument/relationships}id"
EXIT_USAGE = 2
EXIT_UNREADABLE = 1


class ExtractError(Exception):
    pass


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(element: ElementTree.Element, name: str) -> Iterator[ElementTree.Element]:
    return (child for child in element if local_name(child.tag) == name)


def descendants(element: ElementTree.Element, name: str) -> Iterator[ElementTree.Element]:
    return (node for node in element.iter() if local_name(node.tag) == name)


def first_child(element: ElementTree.Element, name: str) -> Optional[ElementTree.Element]:
    return next(children(element, name), None)


def clean_cell(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return LINE_BREAK_MARK.join(line for line in lines if line).replace("|", "\\|")


def read_xml(archive: zipfile.ZipFile, member: str) -> ElementTree.Element:
    try:
        return ElementTree.fromstring(archive.read(member))
    except KeyError as error:
        raise ExtractError(f"The file is missing {member}.") from error
    except ElementTree.ParseError as error:
        raise ExtractError(f"{member} is not valid XML.") from error


def open_archive(path: Path) -> zipfile.ZipFile:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ExtractError("The file is over 5 MB. Split it into smaller files.")
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile as error:
        raise ExtractError("The file is not a valid Office file.") from error
    if sum(member.file_size for member in archive.infolist()) > MAX_UNPACKED_BYTES:
        archive.close()
        raise ExtractError("The file unpacks to more than 100 MB.")
    return archive


def column_number(letters: str) -> int:
    number = 0
    for letter in letters:
        number = number * 26 + ord(letter) - ord("A") + 1
    return number


def split_reference(reference: str) -> Tuple[int, int]:
    match = CELL_REFERENCE.match(reference.replace("$", "").upper())
    if match is None:
        raise ExtractError(f"Unknown cell reference {reference}.")
    return int(match.group(2)), column_number(match.group(1))


def rich_text(element: ElementTree.Element) -> str:
    return "".join(node.text or "" for node in descendants(element, "t"))


def read_shared_strings(archive: zipfile.ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = read_xml(archive, "xl/sharedStrings.xml")
    return [rich_text(item) for item in children(root, "si")]


def relationship_targets(archive: zipfile.ZipFile, rels_member: str, base_folder: str) -> Dict[str, str]:
    if rels_member not in archive.namelist():
        return {}
    targets = {}
    for relationship in descendants(read_xml(archive, rels_member), "Relationship"):
        target = relationship.get("Target", "")
        path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(base_folder, target))
        targets[relationship.get("Id", "")] = path
    return targets


def cell_value(cell: ElementTree.Element, shared_strings: List[str]) -> str:
    cell_type = cell.get("t", "n")
    if cell_type == "inlineStr":
        inline = first_child(cell, "is")
        return "" if inline is None else rich_text(inline)
    value = first_child(cell, "v")
    text = "" if value is None or value.text is None else value.text
    if cell_type == "s":
        index = int(text) if text.isdigit() else -1
        return shared_strings[index] if 0 <= index < len(shared_strings) else ""
    if cell_type == "b":
        return "TRUE" if text == "1" else "FALSE"
    return text


def read_sheet_cells(root: ElementTree.Element, shared_strings: List[str]) -> Dict[Tuple[int, int], str]:
    cells: Dict[Tuple[int, int], str] = {}
    for row_number, row in enumerate(descendants(root, "row"), 1):
        row_index = int(row.get("r", row_number))
        for column_index, cell in enumerate(children(row, "c"), 1):
            reference = cell.get("r")
            position = split_reference(reference) if reference else (row_index, column_index)
            text = clean_cell(cell_value(cell, shared_strings))
            if text:
                cells[position] = text
    for merge in descendants(root, "mergeCell"):
        start, _, end = merge.get("ref", "").partition(":")
        if not start or not end:
            continue
        top, left = split_reference(start)
        bottom, right = split_reference(end)
        value = cells.get((top, left))
        if value is None:
            continue
        for row_index in range(top, bottom + 1):
            for column_index in range(left, right + 1):
                cells[(row_index, column_index)] = value
    return cells


def format_rows(cells: Dict[Tuple[int, int], str]) -> List[str]:
    rows: Dict[int, Dict[int, str]] = {}
    for (row_index, column_index), text in cells.items():
        rows.setdefault(row_index, {})[column_index] = text
    lines = []
    for row_index in sorted(rows):
        row = rows[row_index]
        values = [row.get(column_index, "") for column_index in range(1, max(row) + 1)]
        lines.append(f"row {row_index}: {CELL_SEPARATOR.join(values)}")
    return lines


def extract_xlsx(path: Path) -> List[str]:
    with open_archive(path) as archive:
        shared_strings = read_shared_strings(archive)
        targets = relationship_targets(archive, "xl/_rels/workbook.xml.rels", "xl")
        workbook = read_xml(archive, "xl/workbook.xml")
        output: List[str] = []
        row_count = 0
        for sheet in descendants(workbook, "sheet"):
            name = sheet.get("name", "")
            relationship_id = sheet.get(OFFICE_RELATIONSHIP_ID) or sheet.get(STRICT_RELATIONSHIP_ID) or ""
            member = targets.get(relationship_id)
            if member is None:
                continue
            hidden = " (hidden)" if sheet.get("state") in ("hidden", "veryHidden") else ""
            rows = format_rows(read_sheet_cells(read_xml(archive, member), shared_strings))
            row_count += len(rows)
            if row_count > MAX_ROWS:
                raise ExtractError("The file has more than 5000 rows. Split it into smaller files.")
            output.append(f"=== Sheet: {name}{hidden} ===")
            output.extend(rows or ["(empty)"])
            output.append("")
        return output


def paragraph_text(paragraph: ElementTree.Element) -> str:
    parts = []
    for node in paragraph.iter():
        name = local_name(node.tag)
        if name == "t":
            parts.append(node.text or "")
        elif name == "tab":
            parts.append(" ")
        elif name in ("br", "cr"):
            parts.append("\n")
    return "".join(parts)


def paragraph_prefix(paragraph: ElementTree.Element) -> str:
    properties = first_child(paragraph, "pPr")
    if properties is None:
        return ""
    style = first_child(properties, "pStyle")
    style_name = "" if style is None else next(iter(style.attrib.values()), "")
    if style_name.lower().startswith("heading") or style_name.lower() == "title":
        return "# "
    return "- " if first_child(properties, "numPr") is not None else ""


def table_lines(table: ElementTree.Element, table_number: int) -> List[str]:
    lines = [f"[table {table_number}]"]
    for row_number, row in enumerate(children(table, "tr"), 1):
        cells = [
            clean_cell("\n".join(paragraph_text(paragraph) for paragraph in descendants(cell, "p")))
            for cell in children(row, "tc")
        ]
        lines.append(f"row {row_number}: {CELL_SEPARATOR.join(cells)}")
    lines.append("")
    return lines


def extract_docx(path: Path) -> List[str]:
    with open_archive(path) as archive:
        document = read_xml(archive, "word/document.xml")
    body = first_child(document, "body")
    if body is None:
        raise ExtractError("The document has no body.")
    output = ["=== Document ==="]
    table_count = 0
    row_count = 0
    for element in body:
        name = local_name(element.tag)
        if name == "p":
            text = paragraph_text(element).strip()
            if text:
                output.append(paragraph_prefix(element) + text.replace("\n", LINE_BREAK_MARK))
        elif name == "tbl":
            table_count += 1
            lines = table_lines(element, table_count)
            row_count += len(lines) - 2
            if row_count > MAX_ROWS:
                raise ExtractError("The file has more than 5000 table rows. Split it into smaller files.")
            output.extend(lines)
    return output


EXTRACTORS = {".xlsx": extract_xlsx, ".docx": extract_docx}


def main(arguments: List[str]) -> int:
    if len(arguments) != 1:
        print("Usage: python3 extract_file.py <file.xlsx|file.docx>", file=sys.stderr)
        return EXIT_USAGE
    path = Path(arguments[0]).expanduser()
    extractor = EXTRACTORS.get(path.suffix.lower())
    if extractor is None:
        print(f"{path.suffix or 'This file'} is not .xlsx or .docx: read the file directly.", file=sys.stderr)
        return EXIT_USAGE
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return EXIT_UNREADABLE
    try:
        lines = extractor(path)
    except ExtractError as error:
        print(str(error), file=sys.stderr)
        return EXIT_UNREADABLE
    print("\n".join(lines).rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
