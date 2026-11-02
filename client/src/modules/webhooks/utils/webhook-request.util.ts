import { EMPTY_WEBHOOK_FORM_VALUES, WEBHOOK_EVENTS } from "../typing/constants/webhook.constant";
import type { WebhookFormValues } from "../typing/types/webhook-form-values.type";
import type {
  CreateWebhookRequest,
  UpdateWebhookRequest,
  Webhook,
  WebhookEvent,
} from "../typing/types/webhook.type";

const sortWebhookEvents = (events: readonly WebhookEvent[]): WebhookEvent[] => {
  return WEBHOOK_EVENTS.filter((event) => {
    return events.includes(event);
  });
};

const toDescription = (value: string): string | null => {
  const description = value.trim();

  return description === "" ? null : description;
};

export const buildWebhookFormValues = (webhook: Webhook | null): WebhookFormValues => {
  if (webhook === null) {
    return { ...EMPTY_WEBHOOK_FORM_VALUES, events: [...EMPTY_WEBHOOK_FORM_VALUES.events] };
  }

  return {
    url: webhook.url,
    description: webhook.description ?? "",
    events: sortWebhookEvents(webhook.events),
    isActive: webhook.isActive,
  };
};

export const buildCreateWebhookRequest = (values: WebhookFormValues): CreateWebhookRequest => {
  return {
    url: values.url.trim(),
    description: toDescription(values.description),
    events: sortWebhookEvents(values.events),
    isActive: values.isActive,
  };
};

export const buildUpdateWebhookRequest = (
  values: WebhookFormValues,
  webhook: Webhook,
): Partial<UpdateWebhookRequest> => {
  const body: Partial<UpdateWebhookRequest> = {};
  const url = values.url.trim();
  const description = toDescription(values.description);
  const events = sortWebhookEvents(values.events);

  if (url !== webhook.url) {
    body.url = url;
  }

  if (description !== webhook.description) {
    body.description = description;
  }

  if (events.join(",") !== sortWebhookEvents(webhook.events).join(",")) {
    body.events = events;
  }

  if (values.isActive !== webhook.isActive) {
    body.isActive = values.isActive;
  }

  return body;
};

export const toggleWebhookEvent = (
  events: readonly WebhookEvent[],
  event: WebhookEvent,
  isChosen: boolean,
): WebhookEvent[] => {
  const otherEvents = events.filter((chosenEvent) => {
    return chosenEvent !== event;
  });

  return sortWebhookEvents(isChosen ? [...otherEvents, event] : otherEvents);
};
