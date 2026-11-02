from app.modules.run_logs.domains.run_log.entity import RunLog
from app.modules.run_logs.domains.run_log_entry.entity import RunLogEntry
from app.shared.common import Entity


class RunLogView(Entity):
    run_log: RunLog | None
    entries: list[RunLogEntry]
