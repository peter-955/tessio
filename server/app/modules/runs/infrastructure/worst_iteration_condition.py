from collections.abc import Collection

from sqlalchemy import ColumnElement, SQLColumnExpression, case, select
from sqlalchemy.orm import aliased

from app.modules.runs.infrastructure.case_result_table import CaseResultTable
from app.modules.runs.typing.constants.run_report import WORST_FIRST_RESULT_STATUSES
from app.modules.runs.typing.enums import ResultStatus


def build_result_rank(status: SQLColumnExpression[ResultStatus]) -> ColumnElement[int]:
    return case(
        *((status == result_status, rank) for rank, result_status in enumerate(WORST_FIRST_RESULT_STATUSES)),
        else_=len(WORST_FIRST_RESULT_STATUSES),
    )


def is_worst_iteration(statuses: Collection[ResultStatus] | None = None) -> ColumnElement[bool]:
    sibling = aliased(CaseResultTable)
    statement = select(sibling.id).where(
        sibling.run_id == CaseResultTable.run_id, sibling.test_case_id == CaseResultTable.test_case_id
    )
    if statuses is not None:
        statement = statement.where(sibling.status.in_(statuses))
    worst_id = (
        statement.order_by(build_result_rank(sibling.status), sibling.iteration, sibling.id)
        .limit(1)
        .correlate(CaseResultTable)
        .scalar_subquery()
    )
    return CaseResultTable.id == worst_id
