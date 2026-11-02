import type { Webhook } from "./webhook.type";

export type WebhookModalState =
  | { mode: "closed" }
  | { mode: "create" }
  | { mode: "edit"; webhook: Webhook }
  | { mode: "delete"; webhook: Webhook }
  | { mode: "rotate"; webhook: Webhook }
  | { mode: "deliveries"; webhook: Webhook }
  | { mode: "secret"; webhook: Webhook; secret: string };
