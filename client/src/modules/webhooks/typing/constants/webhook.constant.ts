import type { DSBadgeColor } from "@/components/design-system";
import type { WebhookUrlError } from "../types/webhook-form-error.type";
import type { WebhookFormValues } from "../types/webhook-form-values.type";
import type { WebhookDeliveryStatus, WebhookEvent } from "../types/webhook.type";

export const WEBHOOK_EVENTS: readonly WebhookEvent[] = [
  "run.started",
  "run.finished",
  "failure.opened",
  "failure.status_changed",
  "gap.raised",
  "story.signed_off",
  "plan.signed_off",
];

export const MAX_WEBHOOKS_PER_PROJECT = 20;

export const MAX_WEBHOOK_URL_LENGTH = 2048;

export const MAX_WEBHOOK_DESCRIPTION_LENGTH = 200;

export const WEBHOOK_DELIVERY_LIST_LIMIT = 50;

export const WEBHOOK_URL_PROTOCOL = "https:";

export const WEBHOOK_LOADING_LINE_COUNT = 3;

export const EMPTY_WEBHOOK_FORM_VALUES: WebhookFormValues = {
  url: "",
  description: "",
  events: [...WEBHOOK_EVENTS],
  isActive: true,
};

export const WEBHOOK_DELIVERY_STATUS_COLORS: Record<WebhookDeliveryStatus, DSBadgeColor> = {
  pending: "blue",
  succeeded: "green",
  failed: "red",
};

export const WEBHOOK_EVENT_LABEL_KEYS = {
  "run.started": "runStarted",
  "run.finished": "runFinished",
  "failure.opened": "failureOpened",
  "failure.status_changed": "failureStatusChanged",
  "gap.raised": "gapRaised",
  "story.signed_off": "storySignedOff",
  "plan.signed_off": "planSignedOff",
} as const satisfies Record<WebhookEvent, string>;

export const WEBHOOK_URL_ERROR_KEYS = {
  required: "errors.urlRequired",
  tooLong: "errors.urlTooLong",
  notHttps: "errors.urlNotHttps",
  invalid: "errors.urlInvalid",
} as const satisfies Record<WebhookUrlError, string>;
