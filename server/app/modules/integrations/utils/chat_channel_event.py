from uuid import UUID

from app.shared.events import LiveEvent, LiveEventType


def build_chat_channel_changed_event(project_id: UUID, chat_channel_id: UUID) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.CHAT_CHANNEL_CHANGED, project_id=project_id, ids={"chatChannelId": str(chat_channel_id)}
    )
