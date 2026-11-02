from app.modules.jira.typing.enums import JiraDocumentBlockKind
from app.shared.common import Entity


class JiraDocumentBlock(Entity):
    kind: JiraDocumentBlockKind
    texts: list[str]
    link_url: str | None = None
