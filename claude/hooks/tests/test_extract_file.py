from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Dict, List

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "extract_file.py"
SPREADSHEET_NAMESPACE = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RELATIONSHIP_NAMESPACE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
SHARED_STRINGS = ["Title", "Steps", "Expected", "Pay by card", "Open cart\nPay | confirm", "Paid"]
FIRST_SHEET = """<worksheet xmlns="{ns}"><sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row>
<row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2" t="s"><v>4</v></c><c r="C2" t="s"><v>5</v></c></row>
<row r="3"><c r="B3" t="inlineStr"><is><t>Check the receipt</t></is></c><c r="D3"><v>42</v></c></row>
<row r="4"></row>
<row r="6"><c r="A6" t="b"><v>1</v></c></row>
</sheetData><mergeCells count="1"><mergeCell ref="A2:A3"/></mergeCells></worksheet>""".format(
    ns=SPREADSHEET_NAMESPACE
)
HIDDEN_SHEET = f'<worksheet xmlns="{SPREADSHEET_NAMESPACE}"><sheetData/></worksheet>'
DOCUMENT = """<w:document xmlns:w="{ns}"><w:body>
<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>SHOP-12 Checkout</w:t></w:r></w:p>
<w:p><w:r><w:t>Covers</w:t></w:r><w:r><w:tab/><w:t>AC1</w:t></w:r></w:p>
<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/></w:numPr></w:pPr><w:r><w:t>Signed in</w:t></w:r></w:p>
<w:p></w:p>
<w:tbl>
<w:tr><w:tc><w:p><w:r><w:t>Step</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Expected</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>Open cart</w:t></w:r></w:p><w:p><w:r><w:t>Pay</w:t></w:r></w:p></w:tc>
<w:tc><w:p><w:r><w:t>Paid</w:t></w:r></w:p></w:tc></w:tr>
</w:tbl>
</w:body></w:document>""".format(ns=WORD_NAMESPACE)


def write_zip(path: Path, members: Dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return path


def build_workbook(path: Path, first_sheet: str = FIRST_SHEET) -> Path:
    shared = "".join(f"<si><t>{text}</t></si>" for text in SHARED_STRINGS)
    return write_zip(
        path,
        {
            "xl/workbook.xml": (
                f'<workbook xmlns="{SPREADSHEET_NAMESPACE}" xmlns:r="{RELATIONSHIP_NAMESPACE}"><sheets>'
                '<sheet name="SHOP-12" sheetId="1" r:id="rId1"/>'
                '<sheet name="Old" sheetId="2" state="hidden" r:id="rId2"/>'
                "</sheets></workbook>"
            ),
            "xl/_rels/workbook.xml.rels": (
                f'<Relationships xmlns="{PACKAGE_NAMESPACE}">'
                '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
                '<Relationship Id="rId2" Target="/xl/worksheets/sheet2.xml"/>'
                "</Relationships>"
            ),
            "xl/sharedStrings.xml": f'<sst xmlns="{SPREADSHEET_NAMESPACE}">{shared}</sst>',
            "xl/worksheets/sheet1.xml": first_sheet,
            "xl/worksheets/sheet2.xml": HIDDEN_SHEET,
        },
    )


class ExtractFileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.folder = Path(self.temporary_directory.name)

    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *arguments], capture_output=True, text=True, check=False
        )

    def test_xlsx_prints_every_sheet_with_row_numbers_and_merged_cells(self) -> None:
        workbook = build_workbook(self.folder / "plan.xlsx")

        result = self.run_script(str(workbook))

        self.assertEqual(result.returncode, 0, result.stderr)
        expected: List[str] = [
            "=== Sheet: SHOP-12 ===",
            "row 1: Title | Steps | Expected",
            "row 2: Pay by card | Open cart ⏎ Pay \\| confirm | Paid",
            "row 3: Pay by card | Check the receipt |  | 42",
            "row 6: TRUE",
            "",
            "=== Sheet: Old (hidden) ===",
            "(empty)",
        ]
        self.assertEqual(result.stdout.splitlines(), expected)

    def test_docx_prints_headings_lists_paragraphs_and_tables_in_order(self) -> None:
        document = write_zip(self.folder / "plan.docx", {"word/document.xml": DOCUMENT})

        result = self.run_script(str(document))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "=== Document ===",
                "# SHOP-12 Checkout",
                "Covers AC1",
                "- Signed in",
                "[table 1]",
                "row 1: Step | Expected",
                "row 2: Open cart ⏎ Pay | Paid",
            ],
        )

    def test_other_formats_are_sent_back_to_be_read_directly(self) -> None:
        sheet = self.folder / "plan.csv"
        sheet.write_text("Title,Step\n")

        result = self.run_script(str(sheet))

        self.assertEqual(result.returncode, 2)
        self.assertIn("read the file directly", result.stderr)

    def test_a_missing_file_is_reported(self) -> None:
        result = self.run_script(str(self.folder / "missing.xlsx"))

        self.assertEqual(result.returncode, 1)
        self.assertIn("File not found", result.stderr)

    def test_a_file_that_is_not_an_office_file_is_reported(self) -> None:
        broken = self.folder / "broken.xlsx"
        broken.write_text("not a zip")

        result = self.run_script(str(broken))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "The file is not a valid Office file.")

    def test_a_file_over_five_megabytes_is_refused(self) -> None:
        large = self.folder / "large.xlsx"
        large.write_bytes(b"0" * (5 * 1024 * 1024 + 1))

        result = self.run_script(str(large))

        self.assertEqual(result.returncode, 1)
        self.assertIn("over 5 MB", result.stderr)

    def test_a_sheet_over_five_thousand_rows_is_refused(self) -> None:
        rows = "".join(f'<row r="{n}"><c r="A{n}" t="inlineStr"><is><t>Row</t></is></c></row>' for n in range(1, 5002))
        sheet = f'<worksheet xmlns="{SPREADSHEET_NAMESPACE}"><sheetData>{rows}</sheetData></worksheet>'
        workbook = build_workbook(self.folder / "big.xlsx", sheet)

        result = self.run_script(str(workbook))

        self.assertEqual(result.returncode, 1)
        self.assertIn("more than 5000 rows", result.stderr)

    def test_usage_is_printed_without_a_file(self) -> None:
        result = self.run_script()

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
