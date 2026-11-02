import type { ChatChannel } from "../../typing/types/chat-channel.type";

export const RESULTS_CHANNEL_ID = "7b0e9f1a-3c2d-4e5f-8a9b-0c1d2e3f4a50";

export const RELEASES_CHANNEL_ID = "2c4e6a8b-1d3f-4a5c-9e7b-0f2a4c6e8d10";

export const buildChatChannel = (overrides: Partial<ChatChannel> = {}): ChatChannel => {
  return {
    id: RESULTS_CHANNEL_ID,
    kind: "slack",
    name: "#qa-results",
    webhookUrlMasked: "https://hooks.slack.com/…9876",
    events: ["run.finished", "failure.opened"],
    isActive: true,
    lastDeliveryStatus: null,
    lastDeliveryAt: null,
    lastDeliveryError: null,
    createdAt: "2026-11-01T09:00:00Z",
    ...overrides,
  };
};
