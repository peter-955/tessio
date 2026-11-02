import type { ChatChannelEvent, ChatChannelKind } from "./chat-channel.type";

export interface ChatChannelFormValues {
  kind: ChatChannelKind;
  name: string;
  webhookUrl: string;
  events: ChatChannelEvent[];
  isActive: boolean;
}
