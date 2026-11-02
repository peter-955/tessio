from enum import StrEnum


class JiraDocumentBlockKind(StrEnum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    ORDERED_LIST = "ordered_list"
    BULLET_LIST = "bullet_list"
    CODE = "code"
    LINK = "link"
