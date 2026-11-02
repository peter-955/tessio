import type { WebhookEvent } from "./webhook.type";

export interface WebhookFormValues {
  url: string;
  description: string;
  events: WebhookEvent[];
  isActive: boolean;
}
