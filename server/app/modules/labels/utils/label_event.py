from app.modules.labels.domains.label.entity import Label
from app.shared.events import LiveEvent, LiveEventType


def build_label_changed_event(label: Label) -> LiveEvent:
    return LiveEvent(type=LiveEventType.LABEL_CHANGED, project_id=label.project_id, ids={"labelId": str(label.id)})
