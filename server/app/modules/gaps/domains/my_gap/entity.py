from app.modules.gaps.domains.gap_case.entity import GapCase
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.domains.similar_answer.entity import SimilarAnswer
from app.shared.common import Entity


class MyGap(Entity):
    view: GapView
    criterion_text: str | None
    case: GapCase | None
    similar_answers: list[SimilarAnswer]
