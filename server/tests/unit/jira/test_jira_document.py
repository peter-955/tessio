from app.modules.jira import (
    JiraDocumentBlock,
    JiraDocumentBlockKind,
    build_adf_document,
    clean_jira_summary,
    render_jira_document_text,
)

BLOCKS = [
    JiraDocumentBlock(kind=JiraDocumentBlockKind.HEADING, texts=["Steps to reproduce"]),
    JiraDocumentBlock(kind=JiraDocumentBlockKind.ORDERED_LIST, texts=["Open the cart", "  ", "Pay by card"]),
    JiraDocumentBlock(kind=JiraDocumentBlockKind.PARAGRAPH, texts=["The payment failed."]),
    JiraDocumentBlock(kind=JiraDocumentBlockKind.CODE, texts=["TimeoutError: 30s"]),
    JiraDocumentBlock(kind=JiraDocumentBlockKind.BULLET_LIST, texts=["Passed: 3 of 4"]),
    JiraDocumentBlock(kind=JiraDocumentBlockKind.LINK, texts=["Open in Tessio"], link_url="https://tessio.test/f/1"),
    JiraDocumentBlock(kind=JiraDocumentBlockKind.PARAGRAPH, texts=[""]),
]


def test_blocks_become_an_atlassian_document_without_empty_text_nodes() -> None:
    document = build_adf_document(BLOCKS)

    assert document == {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Steps to reproduce"}]},
            {
                "type": "orderedList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Open the cart"}]}],
                    },
                    {
                        "type": "listItem",
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Pay by card"}]}],
                    },
                ],
            },
            {"type": "paragraph", "content": [{"type": "text", "text": "The payment failed."}]},
            {"type": "codeBlock", "content": [{"type": "text", "text": "TimeoutError: 30s"}]},
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Passed: 3 of 4"}]}],
                    }
                ],
            },
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "Open in Tessio",
                        "marks": [{"type": "link", "attrs": {"href": "https://tessio.test/f/1"}}],
                    }
                ],
            },
        ],
    }


def test_the_same_blocks_render_as_plain_text_for_the_preview() -> None:
    assert render_jira_document_text(BLOCKS) == (
        "Steps to reproduce\n\n1. Open the cart\n2. Pay by card\n\nThe payment failed.\n\nTimeoutError: 30s"
        "\n\n- Passed: 3 of 4\n\nOpen in Tessio: https://tessio.test/f/1"
    )


def test_a_summary_is_one_line_and_at_most_255_characters() -> None:
    assert clean_jira_summary("TC-1  Pay\nby card") == "TC-1 Pay by card"
    long_summary = clean_jira_summary("x" * 300)
    assert len(long_summary) == 255
    assert long_summary.endswith("…")
