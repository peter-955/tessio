from datetime import date, datetime

from sqlalchemy import ColumnElement, Date, SQLColumnExpression, cast, func


def utc_day(moment: SQLColumnExpression[datetime] | SQLColumnExpression[datetime | None]) -> ColumnElement[date]:
    return cast(func.timezone("UTC", moment), Date)
