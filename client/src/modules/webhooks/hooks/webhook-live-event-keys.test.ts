import { LIVE_EVENT_QUERY_KEYS } from "@/shared/typing/constants/live-event-query-keys.constant";
import { LiveEventType } from "@/shared/typing/enums/live-event-type.enum";
import { describe, expect, it } from "vitest";
import { GET_WEBHOOK_DELIVERIES_KEY } from "./queries/use-get-webhook-deliveries";
import { GET_WEBHOOKS_KEY } from "./queries/use-get-webhooks";

describe("webhook live events", () => {
  it("refreshes the webhooks card and the delivery log on webhook.changed", () => {
    expect(LIVE_EVENT_QUERY_KEYS[LiveEventType.WEBHOOK_CHANGED]).toEqual([
      GET_WEBHOOKS_KEY,
      GET_WEBHOOK_DELIVERIES_KEY,
    ]);
  });
});
