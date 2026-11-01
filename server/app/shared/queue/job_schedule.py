from app.shared.common import Entity
from app.shared.typing.enums import JobName, QueueName


class JobSchedule(Entity):
    scheduler_id: str
    queue_name: QueueName
    job_name: JobName
    cron_pattern: str
    timezone: str = "UTC"
