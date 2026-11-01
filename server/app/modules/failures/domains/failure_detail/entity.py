from app.modules.failures.domains.case_result_history_item.entity import CaseResultHistoryItem
from app.modules.failures.domains.failed_step.entity import FailedStep
from app.modules.failures.domains.failure_event_view.entity import FailureEventView
from app.modules.failures.domains.failure_view.entity import FailureView
from app.shared.common import Entity


class FailureDetail(Entity):
    view: FailureView
    failed_step: FailedStep | None
    results: list[CaseResultHistoryItem]
    events: list[FailureEventView]
