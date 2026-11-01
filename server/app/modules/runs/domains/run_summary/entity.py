from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.shared.common import Entity


class RunSummary(Entity):
    run: Run
    labels: RunLabels
    counts: RunCounts
