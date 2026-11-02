import type { components } from "@/lib/api/openapi.type";

export type ChatChannel = components["schemas"]["ChatChannelResponse"];

export type ChatChannelKind = components["schemas"]["ChatChannelKind"];

export type ChatChannelEvent = components["schemas"]["IntegrationEvent"];

export type ChatDeliveryStatus = components["schemas"]["ChatDeliveryStatus"];

export type CreateChatChannelRequest = components["schemas"]["CreateChatChannelRequest"];

export type UpdateChatChannelRequest = components["schemas"]["UpdateChatChannelRequest"];
