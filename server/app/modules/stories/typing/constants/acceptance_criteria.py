ACCEPTANCE_CRITERIA_MARKERS = (
    "acceptance criteria",
    "critères d'acceptation",
    "criteres d'acceptation",
    "tiêu chí chấp nhận",
)
MARKER_PARAGRAPH_MAX_LENGTH = 60
MARKER_PARAGRAPH_TRAILING_CHARACTERS = ":"
CRITERION_CODE_PREFIX = "AC"
NESTED_ITEM_PREFIX = "- "
LINE_BREAK = "\n"
TYPOGRAPHIC_APOSTROPHE = "\N{RIGHT SINGLE QUOTATION MARK}"
PLAIN_APOSTROPHE = "'"
DEFAULT_HEADING_LEVEL = 1
LIST_NODE_TYPES = frozenset({"bulletList", "orderedList", "taskList"})
CONTAINER_NODE_TYPES = frozenset({"panel", "expand", "nestedExpand", "layoutSection", "layoutColumn", "blockquote"})
HEADING_NODE_TYPE = "heading"
PARAGRAPH_NODE_TYPE = "paragraph"
TEXT_NODE_TYPE = "text"
HARD_BREAK_NODE_TYPE = "hardBreak"
INLINE_CARD_NODE_TYPE = "inlineCard"
ATTRIBUTE_TEXT_NODE_TYPES = frozenset({"mention", "emoji", "status"})
INLINE_NODE_TYPES = frozenset({"text", "hardBreak", "mention", "emoji", "status", "inlineCard", "date"})
