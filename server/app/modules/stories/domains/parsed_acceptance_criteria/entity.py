from app.modules.stories.typing.enums import CriteriaSource
from app.shared.common import Entity


class ParsedAcceptanceCriteria(Entity):
    texts: list[str]
    source: CriteriaSource
