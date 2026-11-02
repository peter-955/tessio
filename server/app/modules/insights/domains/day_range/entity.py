from datetime import date, timedelta

from app.shared.common import Entity


class DayRange(Entity):
    first_day: date
    last_day: date

    @property
    def days(self) -> list[date]:
        return [self.first_day + timedelta(days=offset) for offset in range((self.last_day - self.first_day).days + 1)]

    def contains(self, day: date) -> bool:
        return self.first_day <= day <= self.last_day
