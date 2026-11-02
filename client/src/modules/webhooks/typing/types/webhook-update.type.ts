import type { UpdateWebhookRequest } from "./webhook.type";

export interface WebhookUpdate {
  webhookId: string;
  body: Partial<UpdateWebhookRequest>;
}
