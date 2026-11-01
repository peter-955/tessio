import csv
from io import BytesIO, StringIO
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile, LargeZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from app.modules.test_cases.domains.case_import_skip.entity import CaseImportSkip
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.parsed_case_import.entity import ParsedCaseImport
from app.modules.test_cases.errors import ImportInvalidFileError
from app.modules.test_cases.typing.constants import (
    CSV_DELIMITERS,
    CSV_FILE_EXTENSIONS,
    CSV_SNIFF_SAMPLE_LENGTH,
    MAX_IMPORT_ROWS,
    MAX_IMPORTED_CASES,
    XLSX_FILE_EXTENSIONS,
)
from app.modules.test_cases.typing.enums import CaseImportFormat, CaseImportSkipReason
from app.modules.test_cases.utils.case_import_rows import parse_case_rows


def detect_case_import_format(file_name: str) -> CaseImportFormat:
    base_name = file_name.replace("\\", "/").rsplit("/", 1)[-1].strip().lower()
    if base_name.endswith(XLSX_FILE_EXTENSIONS):
        return CaseImportFormat.XLSX
    if base_name.endswith(CSV_FILE_EXTENSIONS):
        return CaseImportFormat.CSV
    raise ImportInvalidFileError


def parse_xlsx(content: bytes) -> tuple[list[ImportedCase], list[CaseImportSkip]]:
    cases: list[ImportedCase] = []
    skipped: list[CaseImportSkip] = []
    row_count = 0
    try:
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
        try:
            for worksheet in workbook.worksheets:
                sheet_name = worksheet.title.strip()
                sheet = parse_case_rows(
                    worksheet.iter_rows(values_only=True),
                    sheet_name,
                    sheet_name.upper() or None,
                    MAX_IMPORT_ROWS - row_count,
                )
                if sheet is None:
                    skipped.append(
                        CaseImportSkip(location=sheet_name, reason=CaseImportSkipReason.SHEET_WITHOUT_HEADER)
                    )
                    continue
                row_count += sheet.row_count
                cases.extend(sheet.cases)
                skipped.extend(sheet.skipped)
        finally:
            workbook.close()
    except (
        BadZipFile,
        LargeZipFile,
        InvalidFileException,
        ParseError,
        KeyError,
        OSError,
        ValueError,
        TypeError,
        NotImplementedError,
    ) as error:
        raise ImportInvalidFileError from error
    return cases, skipped


def parse_csv(content: bytes) -> tuple[list[ImportedCase], list[CaseImportSkip]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ImportInvalidFileError from error
    dialect: type[csv.Dialect]
    try:
        dialect = csv.Sniffer().sniff(text[:CSV_SNIFF_SAMPLE_LENGTH], delimiters=CSV_DELIMITERS)
    except csv.Error:
        dialect = csv.excel
    try:
        sheet = parse_case_rows(csv.reader(StringIO(text), dialect), None, None, MAX_IMPORT_ROWS)
    except csv.Error as error:
        raise ImportInvalidFileError from error
    if sheet is None:
        raise ImportInvalidFileError
    return sheet.cases, sheet.skipped


def parse_case_import(file_name: str, content: bytes) -> ParsedCaseImport:
    import_format = detect_case_import_format(file_name)
    cases, skipped = parse_xlsx(content) if import_format is CaseImportFormat.XLSX else parse_csv(content)
    if len(cases) > MAX_IMPORTED_CASES:
        raise ImportInvalidFileError
    return ParsedCaseImport(format=import_format, cases=cases, skipped=skipped)
