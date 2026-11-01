from uuid import UUID

from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_detail.entity import RunCaseDetail
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.shared.common import Entity


class RunDetail(Entity):
    run: Run
    labels: RunLabels
    cases: list[RunCaseDetail]
    child_run_ids: list[UUID]
