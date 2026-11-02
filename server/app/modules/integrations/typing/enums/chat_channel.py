from enum import StrEnum


class ChatChannelKind(StrEnum):
    SLACK = "slack"
    TEAMS = "teams"


class ChatDeliveryStatus(StrEnum):
    DELIVERED = "delivered"
    FAILED = "failed"
