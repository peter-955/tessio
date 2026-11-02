import os

import pytest

from app.modules.reports.infrastructure import WeasyPrintPdfRenderer
from app.modules.reports.utils.html_report import render_html
from app.modules.users import UserLanguage
from tests.unit.reports.report_document_samples import build_sample_document

PANGO_MISSING_REASON = "Pango not installed: brew install pango"


async def test_weasyprint_renders_a_real_pdf() -> None:
    html = render_html(build_sample_document(), UserLanguage.VI)
    try:
        pdf = await WeasyPrintPdfRenderer().render(html)
    except OSError as error:
        if os.environ.get("CI"):
            pytest.fail(f"WeasyPrint cannot load its system libraries in CI: {error}")
        pytest.skip(PANGO_MISSING_REASON)

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
