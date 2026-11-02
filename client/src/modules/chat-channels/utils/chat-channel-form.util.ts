import {
  CHAT_CHANNEL_EVENTS,
  CHAT_WEBHOOK_URL_PROTOCOL,
  DEFAULT_CHAT_CHANNEL_EVENTS,
  DEFAULT_CHAT_CHANNEL_KIND,
  MAX_CHAT_CHANNEL_NAME_LENGTH,
  MAX_CHAT_WEBHOOK_URL_LENGTH,
} from "../typing/constants/chat-channel.constant";
import type {
  ChatChannelEventsError,
  ChatChannelNameError,
  ChatWebhookUrlError,
} from "../typing/types/chat-channel-form-error.type";
import type { ChatChannelFormValues } from "../typing/types/chat-channel-form-values.type";
import type {
  ChatChannel,
  ChatChannelEvent,
  CreateChatChannelRequest,
  UpdateChatChannelRequest,
} from "../typing/types/chat-channel.type";

export const sortChatChannelEvents = (events: readonly ChatChannelEvent[]): ChatChannelEvent[] => {
  return CHAT_CHANNEL_EVENTS.filter((event) => events.includes(event));
};

export const toggleChatChannelEvent = (
  events: readonly ChatChannelEvent[],
  event: ChatChannelEvent,
  isOn: boolean,
): ChatChannelEvent[] => {
  const otherEvents = events.filter((candidate) => candidate !== event);

  return sortChatChannelEvents(isOn ? [...otherEvents, event] : otherEvents);
};

export const buildChatChannelFormValues = (
  chatChannel: ChatChannel | null,
): ChatChannelFormValues => {
  if (chatChannel === null) {
    return {
      kind: DEFAULT_CHAT_CHANNEL_KIND,
      name: "",
      webhookUrl: "",
      events: [...DEFAULT_CHAT_CHANNEL_EVENTS],
      isActive: true,
    };
  }

  return {
    kind: chatChannel.kind,
    name: chatChannel.name,
    webhookUrl: "",
    events: sortChatChannelEvents(chatChannel.events),
    isActive: chatChannel.isActive,
  };
};

export const findChatChannelNameError = (
  name: string,
  chatChannels: readonly ChatChannel[],
  chatChannelId: string | null,
): ChatChannelNameError | null => {
  const trimmedName = name.trim();

  if (trimmedName === "") {
    return "nameRequired";
  }

  if (trimmedName.length > MAX_CHAT_CHANNEL_NAME_LENGTH) {
    return "nameTooLong";
  }

  const lowerName = trimmedName.toLowerCase();
  const isUsed = chatChannels.some((chatChannel) => {
    return chatChannel.id !== chatChannelId && chatChannel.name.toLowerCase() === lowerName;
  });

  return isUsed ? "nameAlreadyUsed" : null;
};

const isHttpsUrl = (url: string): boolean => {
  try {
    const parsedUrl = new URL(url);

    return parsedUrl.protocol === CHAT_WEBHOOK_URL_PROTOCOL && parsedUrl.hostname !== "";
  } catch {
    return false;
  }
};

export const findChatWebhookUrlError = (
  webhookUrl: string,
  isRequired: boolean,
): ChatWebhookUrlError | null => {
  const trimmedUrl = webhookUrl.trim();

  if (trimmedUrl === "") {
    return isRequired ? "urlRequired" : null;
  }

  if (trimmedUrl.length > MAX_CHAT_WEBHOOK_URL_LENGTH) {
    return "urlTooLong";
  }

  return isHttpsUrl(trimmedUrl) ? null : "urlNotHttps";
};

export const findChatChannelEventsError = (
  events: readonly ChatChannelEvent[],
): ChatChannelEventsError | null => {
  return events.length === 0 ? "eventsRequired" : null;
};

export const buildCreateChatChannelRequest = (
  values: ChatChannelFormValues,
): CreateChatChannelRequest => {
  return {
    kind: values.kind,
    name: values.name.trim(),
    webhookUrl: values.webhookUrl.trim(),
    events: sortChatChannelEvents(values.events),
    isActive: values.isActive,
  };
};

const hasSameEvents = (
  first: readonly ChatChannelEvent[],
  second: readonly ChatChannelEvent[],
): boolean => {
  const sortedFirst = sortChatChannelEvents(first);
  const sortedSecond = sortChatChannelEvents(second);

  return (
    sortedFirst.length === sortedSecond.length &&
    sortedFirst.every((event, index) => event === sortedSecond[index])
  );
};

export const buildUpdateChatChannelRequest = (
  values: ChatChannelFormValues,
  chatChannel: ChatChannel,
): UpdateChatChannelRequest => {
  const name = values.name.trim();
  const webhookUrl = values.webhookUrl.trim();
  const events = sortChatChannelEvents(values.events);

  return {
    ...(name === chatChannel.name ? {} : { name }),
    ...(webhookUrl === "" ? {} : { webhookUrl }),
    ...(hasSameEvents(events, chatChannel.events) ? {} : { events }),
    ...(values.isActive === chatChannel.isActive ? {} : { isActive: values.isActive }),
  };
};
