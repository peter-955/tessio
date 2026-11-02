from datetime import datetime

from app.shared.common import Entity


class GapSpan(Entity):
    created_at: datetime
    answered_at: datetime | None
    reopened_at: datetime | None
    is_open: bool

    def is_open_at(self, moment: datetime) -> bool:
        if self.created_at >= moment:
            return False
        if self.answered_at is None or self.answered_at >= moment:
            return True
        return self.is_open and self.reopened_at is not None and self.reopened_at < moment
