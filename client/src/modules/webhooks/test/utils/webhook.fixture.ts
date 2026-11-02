import {
  ADMIN_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import type { Project } from "@/components/project-context/typing/types/project.type";
import type { Webhook, WebhookDelivery } from "../../typing/types/webhook.type";

export const WEBHOOK_ID = "7b000000-0000-4000-8000-000000000001";

export const DELIVERY_ID = "7c000000-0000-4000-8000-000000000001";

export const WEBHOOK_SECRET = "whsec_n3wS3cretValue";

export const buildWebhookDelivery = (overrides: Partial<WebhookDelivery> = {}): WebhookDelivery => {
  return {
    id: DELIVERY_ID,
    webhookId: WEBHOOK_ID,
    event: "run.finished",
    status: "failed",
    attempts: 5,
    responseStatus: 500,
    error: "The receiver answered HTTP 500.",
    redeliveryOfId: null,
    lastAttemptAt: "2026-11-02T10:20:00Z",
    deliveredAt: null,
    createdAt: "2026-11-02T10:15:00Z",
    payload: {
      id: "0193-event",
      event: "run.finished",
      data: { runId: "a6000000-0000-4000-8000-000000000001", status: "failed" },
    },
    ...overrides,
  };
};

export const buildWebhook = (overrides: Partial<Webhook> = {}): Webhook => {
  return {
    id: WEBHOOK_ID,
    url: "https://ci.example.com/hooks/tessio",
    description: "Release dashboard",
    events: ["run.started", "run.finished"],
    isActive: true,
    secretHint: "whsec_…a1b2",
    createdAt: "2026-11-01T09:00:00Z",
    lastDelivery: buildWebhookDelivery(),
    ...overrides,
  };
};

export const buildIntegrationAdminProject = (overrides: Partial<Project> = {}): Project => {
  return buildProject({
    myRole: "admin",
    capabilities: [...ADMIN_CAPABILITIES, "integration.manage"],
    ...overrides,
  });
};
