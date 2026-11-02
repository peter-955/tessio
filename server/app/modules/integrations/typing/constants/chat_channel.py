import re
from collections.abc import Mapping

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent

MAX_CHAT_CHANNEL_NAME_LENGTH = 80
MAX_CHAT_CHANNELS_PER_PROJECT = 20
MAX_CHAT_WEBHOOK_URL_LENGTH = 2048
MAX_CHAT_DELIVERY_ERROR_LENGTH = 300
CHAT_WEBHOOK_URL_HINT_SUFFIX_LENGTH = 4
CHAT_WEBHOOK_URL_HINT_MIN_PATH_LENGTH = 12
CHAT_WEBHOOK_URL_SCHEME = "https"
BLOCKED_CHAT_HOST_NAMES = frozenset({"localhost"})
BLOCKED_CHAT_HOST_SUFFIXES = (".localhost", ".local", ".internal", ".lan", ".home.arpa")
NUMERIC_HOST_LABEL_PATTERN = re.compile(r"(0x[0-9a-f]*|[0-9]+)", re.IGNORECASE)
CHAT_CASE_CODE_PREFIX = "TC-"
CHAT_MESSAGE_TEXT_LIMIT = 500
CHAT_TITLE_LIMIT = 150
CHAT_LINK_LABEL = "Open in Tessio"
CHAT_TEST_MESSAGE_TITLE = "Tessio test message"
CHAT_TEST_MESSAGE_TEXT = "This channel is connected to the Tessio project {project_name} ({project_key})."
CHAT_TEST_EVENTS_LABEL = "Events"
CHAT_FOOTER_TEMPLATE = "Tessio · {project_name}"
CHAT_EMPTY_VALUE = "-"
CHAT_EVENT_LABELS: Mapping[IntegrationEvent, str] = {
    IntegrationEvent.RUN_STARTED: "Run started",
    IntegrationEvent.RUN_FINISHED: "Run finished",
    IntegrationEvent.FAILURE_OPENED: "Failure opened",
    IntegrationEvent.FAILURE_STATUS_CHANGED: "Failure status changed",
    IntegrationEvent.GAP_RAISED: "Gap raised",
    IntegrationEvent.STORY_SIGNED_OFF: "Story signed off",
    IntegrationEvent.PLAN_SIGNED_OFF: "Plan signed off",
}
CHAT_EXECUTOR_LABELS: Mapping[str, str] = {"claude": "Claude", "manual": "Manual", "script": "Script", "ci": "CI"}
SLACK_HEADER_LIMIT = 150
SLACK_SECTION_LIMIT = 3000
SLACK_FIELD_LIMIT = 2000
SLACK_MAX_FIELDS = 10
TEAMS_CARD_CONTENT_TYPE = "application/vnd.microsoft.card.adaptive"
TEAMS_CARD_SCHEMA = "http://adaptivecards.io/schemas/adaptive-card.json"
TEAMS_CARD_VERSION = "1.4"
