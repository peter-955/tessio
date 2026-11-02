from app.modules.reports.utils.html_report import render_html
from app.modules.reports.utils.markdown_report import render_markdown
from app.modules.reports.utils.report_masking import mask_document
from app.modules.users import UserLanguage
from app.shared.masking import MASKED_VALUE, SecretMasker
from tests.unit.reports.report_document_samples import build_sample_document


def test_markdown_escapes_tables_and_keeps_one_line_per_row() -> None:
    markdown = render_markdown(build_sample_document())

    assert markdown.startswith("# Run report · SHOP-1 Pay \\| refund\n")
    assert "- **Status:** Failed" in markdown
    assert "| Case | Actual result |\n| --- | --- |" in markdown
    assert "| TC-1 | Typed s3cr3t then saw \\*500\\* |" in markdown
    assert "| TC-2 | Thành công · réussi |" in markdown
    assert "_Nothing to show._" in markdown
    assert "\\<script\\>" in markdown


def test_html_escapes_every_text_and_names_the_language() -> None:
    html = render_html(build_sample_document(), UserLanguage.VI)

    assert html.startswith('<!doctype html><html lang="vi">')
    assert "&lt;script&gt;" in html
    assert "<script>" not in html
    assert "<td>Thành công · réussi</td>" in html
    assert '<p class="empty">Nothing to show.</p>' in html


def test_masking_replaces_secret_values_in_every_text() -> None:
    masked = mask_document(build_sample_document("s3cr3t"), SecretMasker(["s3cr3t"]))

    rendered = render_markdown(masked) + render_html(masked, UserLanguage.EN)
    assert "s3cr3t" not in rendered
    assert f"Token {MASKED_VALUE} leaked" in rendered
