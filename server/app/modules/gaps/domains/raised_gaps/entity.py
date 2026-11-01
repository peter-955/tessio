from app.modules.gaps.domains.gap_view.entity import GapView
from app.shared.common import Entity


class RaisedGaps(Entity):
    gaps: list[GapView]
    open_gap_count: int

    @property
    def is_ready(self) -> bool:
        return self.open_gap_count == 0
