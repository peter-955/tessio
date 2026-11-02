import { describe, expect, it } from "vitest";
import { buildWebhook } from "../test/utils/webhook.fixture";
import { WEBHOOK_EVENTS } from "../typing/constants/webhook.constant";
import {
  buildCreateWebhookRequest,
  buildUpdateWebhookRequest,
  buildWebhookFormValues,
  toggleWebhookEvent,
} from "./webhook-request.util";

describe("webhook requests", () => {
  it("starts a new webhook with every event chosen and active", () => {
    expect(buildWebhookFormValues(null)).toEqual({
      url: "",
      description: "",
      events: [...WEBHOOK_EVENTS],
      isActive: true,
    });
  });

  it("trims the URL, sends no empty description and keeps the events in a fixed order", () => {
    expect(
      buildCreateWebhookRequest({
        url: " https://ci.example.com/hook ",
        description: "  ",
        events: ["plan.signed_off", "run.started"],
        isActive: false,
      }),
    ).toEqual({
      url: "https://ci.example.com/hook",
      description: null,
      events: ["run.started", "plan.signed_off"],
      isActive: false,
    });
  });

  it("patches only the changed fields", () => {
    const webhook = buildWebhook();
    const values = buildWebhookFormValues(webhook);

    expect(buildUpdateWebhookRequest(values, webhook)).toEqual({});
    expect(
      buildUpdateWebhookRequest(
        { ...values, description: "", events: ["run.finished", "run.started"] },
        webhook,
      ),
    ).toEqual({ description: null });
    expect(
      buildUpdateWebhookRequest(
        { ...values, url: "https://hooks.example.com/x", events: ["gap.raised"], isActive: false },
        webhook,
      ),
    ).toEqual({ url: "https://hooks.example.com/x", events: ["gap.raised"], isActive: false });
  });

  it("adds and removes an event", () => {
    expect(toggleWebhookEvent(["run.finished"], "run.started", true)).toEqual([
      "run.started",
      "run.finished",
    ]);
    expect(toggleWebhookEvent(["run.started", "run.finished"], "run.started", false)).toEqual([
      "run.finished",
    ]);
  });
});
