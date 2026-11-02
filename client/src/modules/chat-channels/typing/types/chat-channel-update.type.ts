import type { UpdateChatChannelRequest } from "./chat-channel.type";

export interface ChatChannelUpdate {
  chatChannelId: string;
  body: UpdateChatChannelRequest;
}
