import { MAX_WEBHOOK_URL_LENGTH, WEBHOOK_URL_PROTOCOL } from "../typing/constants/webhook.constant";
import type { WebhookUrlError } from "../typing/types/webhook-form-error.type";

const parseUrl = (value: string): URL | null => {
  try {
    return new URL(value);
  } catch {
    return null;
  }
};

export const findWebhookUrlError = (value: string): WebhookUrlError | null => {
  const url = value.trim();
  if (url === "") {
    return "required";
  }

  if (url.length > MAX_WEBHOOK_URL_LENGTH) {
    return "tooLong";
  }

  const parsedUrl = parseUrl(url);
  if (parsedUrl === null || /\s/.test(url)) {
    return "invalid";
  }

  if (parsedUrl.protocol !== WEBHOOK_URL_PROTOCOL) {
    return "notHttps";
  }

  const hasCredentials = parsedUrl.username !== "" || parsedUrl.password !== "";
  if (!parsedUrl.hostname.includes(".") || hasCredentials) {
    return "invalid";
  }

  return null;
};
