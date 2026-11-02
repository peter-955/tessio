from uuid import UUID

from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob


def read_job_id(job: ChatDeliveryJob, key: str) -> UUID | None:
    value = job.ids.get(key)
    if value is None:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None
