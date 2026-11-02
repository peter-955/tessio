import type { components } from "@/lib/api/openapi.type";

export type Webhook = components["schemas"]["WebhookResponse"];

export type WebhookDelivery = components["schemas"]["WebhookDeliveryResponse"];

export type WebhookWithSecret = components["schemas"]["WebhookWithSecretResponse"];

export type WebhookEvent = components["schemas"]["IntegrationEvent"];

export type WebhookDeliveryStatus = components["schemas"]["WebhookDeliveryStatus"];

export type CreateWebhookRequest = components["schemas"]["CreateWebhookRequest"];

export type UpdateWebhookRequest = components["schemas"]["UpdateWebhookRequest"];
