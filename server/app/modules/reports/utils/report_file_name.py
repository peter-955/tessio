import re
import unicodedata

from app.modules.notifications import ReportFormat
from app.modules.reports.typing.constants import MAX_FILE_NAME_STEM_LENGTH

UNSAFE_FILE_NAME_CHARACTERS = re.compile(r"[^A-Za-z0-9._-]+")


def build_report_file_name(stem: str, report_format: ReportFormat) -> str:
    ascii_stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    safe_stem = UNSAFE_FILE_NAME_CHARACTERS.sub("-", ascii_stem).strip("-.")[:MAX_FILE_NAME_STEM_LENGTH].strip("-.")
    return f"{safe_stem or 'report'}.{report_format.value}"
