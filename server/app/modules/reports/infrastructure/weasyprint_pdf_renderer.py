import importlib

import anyio.to_thread

from app.modules.reports.ports.pdf_renderer import PdfRenderer

WEASYPRINT_MODULE = "weasyprint"


def render_pdf_blocking(html: str) -> bytes:
    weasyprint = importlib.import_module(WEASYPRINT_MODULE)
    pdf: bytes = weasyprint.HTML(string=html).write_pdf()
    return pdf


class WeasyPrintPdfRenderer(PdfRenderer):
    async def render(self, html: str) -> bytes:
        return await anyio.to_thread.run_sync(render_pdf_blocking, html)
