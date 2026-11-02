import type { ChatChannel } from "./chat-channel.type";

export type ChatChannelModalState =
  | { mode: "closed" }
  | { mode: "create" }
  | { mode: "edit"; chatChannel: ChatChannel }
  | { mode: "delete"; chatChannel: ChatChannel };
