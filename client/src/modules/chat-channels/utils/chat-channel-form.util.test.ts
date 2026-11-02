import { describe, expect, it } from "vitest";
import { buildChatChannel, RELEASES_CHANNEL_ID } from "../test/utils/chat-channel-fixture.util";
import {
  buildChatChannelFormValues,
  buildCreateChatChannelRequest,
  buildUpdateChatChannelRequest,
  findChatChannelEventsError,
  findChatChannelNameError,
  findChatWebhookUrlError,
  toggleChatChannelEvent,
} from "./chat-channel-form.util";

describe("chat channel form", () => {
  it("starts a new channel as an active Slack channel with the default events", () => {
    expect(buildChatChannelFormValues(null)).toEqual({
      kind: "slack",
      name: "",
      webhookUrl: "",
      events: ["run.finished", "failure.opened"],
      isActive: true,
    });
  });

  it("never fills the saved URL into the edit form", () => {
    const values = buildChatChannelFormValues(buildChatChannel({ kind: "teams" }));

    expect(values.webhookUrl).toBe("");
    expect(values.kind).toBe("teams");
  });

  it("refuses an empty, too long or already used name, in any case", () => {
    const channels = [buildChatChannel()];

    expect(findChatChannelNameError("  ", channels, null)).toBe("nameRequired");
    expect(findChatChannelNameError("a".repeat(81), channels, null)).toBe("nameTooLong");
    expect(findChatChannelNameError(" #QA-Results ", channels, null)).toBe("nameAlreadyUsed");
    expect(findChatChannelNameError("#QA-Results", channels, channels[0].id)).toBeNull();
    expect(findChatChannelNameError("#releases", channels, null)).toBeNull();
  });

  it("asks for an https webhook URL, and lets an edit keep the saved one", () => {
    expect(findChatWebhookUrlError("", true)).toBe("urlRequired");
    expect(findChatWebhookUrlError("", false)).toBeNull();
    expect(findChatWebhookUrlError("http://hooks.slack.com/services/T0/B0/x", true)).toBe(
      "urlNotHttps",
    );
    expect(findChatWebhookUrlError("not a url", true)).toBe("urlNotHttps");
    expect(findChatWebhookUrlError(`https://hooks.slack.com/${"a".repeat(2048)}`, true)).toBe(
      "urlTooLong",
    );
    expect(findChatWebhookUrlError(" https://hooks.slack.com/services/T0/B0/x ", true)).toBeNull();
  });

  it("needs at least one event and keeps the events in the server's order", () => {
    expect(findChatChannelEventsError([])).toBe("eventsRequired");
    expect(toggleChatChannelEvent(["plan.signed_off"], "run.started", true)).toEqual([
      "run.started",
      "plan.signed_off",
    ]);
    expect(toggleChatChannelEvent(["run.started", "gap.raised"], "run.started", false)).toEqual([
      "gap.raised",
    ]);
  });

  it("builds a trimmed create request", () => {
    expect(
      buildCreateChatChannelRequest({
        kind: "teams",
        name: " #releases ",
        webhookUrl: " https://example.webhook.office.com/workflows/abc ",
        events: ["story.signed_off", "run.started"],
        isActive: false,
      }),
    ).toEqual({
      kind: "teams",
      name: "#releases",
      webhookUrl: "https://example.webhook.office.com/workflows/abc",
      events: ["run.started", "story.signed_off"],
      isActive: false,
    });
  });

  it("sends only the changed fields on an edit, and the URL only when a new one is typed", () => {
    const channel = buildChatChannel({ id: RELEASES_CHANNEL_ID });
    const unchanged = buildChatChannelFormValues(channel);

    expect(buildUpdateChatChannelRequest(unchanged, channel)).toEqual({});
    expect(
      buildUpdateChatChannelRequest(
        { ...unchanged, events: ["failure.opened", "run.finished"] },
        channel,
      ),
    ).toEqual({});
    expect(
      buildUpdateChatChannelRequest(
        {
          ...unchanged,
          name: "#qa",
          webhookUrl: "https://hooks.slack.com/services/T0/B0/new",
          events: ["gap.raised"],
          isActive: false,
        },
        channel,
      ),
    ).toEqual({
      name: "#qa",
      webhookUrl: "https://hooks.slack.com/services/T0/B0/new",
      events: ["gap.raised"],
      isActive: false,
    });
  });
});
