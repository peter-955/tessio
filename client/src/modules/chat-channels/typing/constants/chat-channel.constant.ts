import type { ChatChannelEvent, ChatChannelKind } from "../types/chat-channel.type";

export const MAX_CHAT_CHANNEL_NAME_LENGTH = 80;

export const MAX_CHAT_CHANNELS_PER_PROJECT = 20;

export const MAX_CHAT_WEBHOOK_URL_LENGTH = 2048;

export const CHAT_WEBHOOK_URL_PROTOCOL = "https:";

export const CHAT_CHANNEL_KINDS: readonly ChatChannelKind[] = ["slack", "teams"];

export const DEFAULT_CHAT_CHANNEL_KIND: ChatChannelKind = "slack";

export const CHAT_CHANNEL_EVENTS: readonly ChatChannelEvent[] = [
  "run.started",
  "run.finished",
  "failure.opened",
  "failure.status_changed",
  "gap.raised",
  "story.signed_off",
  "plan.signed_off",
];

export const DEFAULT_CHAT_CHANNEL_EVENTS: readonly ChatChannelEvent[] = [
  "run.finished",
  "failure.opened",
];

export const CHAT_CHANNEL_EVENT_KEYS = {
  "run.started": "runStarted",
  "run.finished": "runFinished",
  "failure.opened": "failureOpened",
  "failure.status_changed": "failureStatusChanged",
  "gap.raised": "gapRaised",
  "story.signed_off": "storySignedOff",
  "plan.signed_off": "planSignedOff",
} as const satisfies Readonly<Record<ChatChannelEvent, string>>;
