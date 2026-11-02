import englishChatChannels from "@/lib/i18n/locales/en/chatChannels.json";
import {
  createCreatedResult,
  createErrorResult,
  createNoContentResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/labels/test/utils/api-result.util";
import { buildProject } from "@/modules/labels/test/utils/project-fixture.util";
import { renderWithProject } from "@/modules/labels/test/utils/render-with-project.util";
import { openSelectOption } from "@/modules/labels/test/utils/select-option.util";
import { stubScrollIntoView } from "@/modules/labels/test/utils/stub-scroll-into-view.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiDelete, apiGet, apiPatch, apiPost } from "../../test/mocks/api-client.mock";
import {
  buildChatChannel,
  RELEASES_CHANNEL_ID,
  RESULTS_CHANNEL_ID,
} from "../../test/utils/chat-channel-fixture.util";
import type { ChatChannel } from "../../typing/types/chat-channel.type";
import { ChatChannelsCard } from "./chat-channels-card";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const CHANNELS_PATH = "/api/projects/{project_key}/chat-channels";
const CHANNEL_PATH = "/api/projects/{project_key}/chat-channels/{chat_channel_id}";
const TEST_PATH = "/api/projects/{project_key}/chat-channels/{chat_channel_id}/test";

const { card, form, events, validation, toasts, errors, kinds, delivery } = englishChatChannels;

const results = buildChatChannel({
  lastDeliveryStatus: "delivered",
  lastDeliveryAt: "2026-11-02T08:30:00Z",
});
const releases = buildChatChannel({
  id: RELEASES_CHANNEL_ID,
  kind: "teams",
  name: "#releases",
  webhookUrlMasked: "https://example.webhook.office.com/…ab12",
  events: ["story.signed_off", "plan.signed_off"],
  isActive: false,
  lastDeliveryStatus: "failed",
  lastDeliveryAt: "2026-11-02T09:00:00Z",
  lastDeliveryError: "HTTP 404: the webhook no longer exists",
});

const adminProject = buildProject({
  myRole: "admin",
  capabilities: ["project.view", "project.edit", "integration.manage"],
});

const renderCard = (): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<ChatChannelsCard projectKey="SHOP" />, adminProject);
};

const actionsName = (name: string): string => {
  return card.actionsFor.replace("{{name}}", name);
};

const openRowMenu = async (user: UserEvent, name: string): Promise<void> => {
  await user.click(await screen.findByRole("button", { name: actionsName(name) }));
};

const lastBody = (call: typeof apiPost | typeof apiPatch): unknown => {
  return (call.mock.calls.at(-1)?.[1] as { body: unknown }).body;
};

describe("ChatChannelsCard", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPatch.mockReset();
    apiDelete.mockReset();
    respondWithRoutes(apiGet, { [CHANNELS_PATH]: createSuccessResult([releases, results]) });
  });

  it("lists each channel with its app, masked URL, events and last message", async () => {
    const { container } = renderCard();

    const table = await screen.findByRole("table", { name: card.tableLabel });
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(within(rows[1]).getByText("#releases")).toBeInTheDocument();
    expect(within(rows[1]).getByText(kinds.teams)).toBeInTheDocument();
    expect(within(rows[1]).getByText(card.off)).toBeInTheDocument();
    expect(
      within(rows[1]).getByText("https://example.webhook.office.com/…ab12"),
    ).toBeInTheDocument();
    expect(
      within(rows[1]).getByText(`${events.storySignedOff}, ${events.planSignedOff}`),
    ).toBeInTheDocument();
    expect(within(rows[1]).getByText(delivery.failed)).toBeInTheDocument();
    expect(within(rows[1]).getByText("HTTP 404: the webhook no longer exists")).toBeInTheDocument();
    expect(within(rows[2]).getByText(kinds.slack)).toBeInTheDocument();
    expect(within(rows[2]).getByText(delivery.delivered)).toBeInTheDocument();
    expect(within(rows[2]).queryByText(card.off)).toBeNull();
    expect(screen.queryByText(/hooks\.slack\.com\/services/)).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("says when the project has no channels", async () => {
    respondWithRoutes(apiGet, { [CHANNELS_PATH]: createSuccessResult([]) });
    renderCard();

    expect(await screen.findByText(card.empty)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: card.add })).toBeEnabled();
  });

  it("shows an error with Try again when the channels cannot be loaded", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respondWithRoutes(apiGet, {
      [CHANNELS_PATH]: (): ApiResult => {
        return isFailing ? createErrorResult(500, "CONFLICT") : createSuccessResult([results]);
      },
    });
    renderCard();

    expect(await screen.findByText(card.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: card.retry }));

    expect(await screen.findByText("#qa-results")).toBeInTheDocument();
  });

  it("checks the form before adding a channel", async () => {
    const user = userEvent.setup();
    renderCard();

    await user.click(await screen.findByRole("button", { name: card.add }));
    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByRole("checkbox", { name: events.runFinished }));
    await user.click(within(dialog).getByRole("checkbox", { name: events.failureOpened }));
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), "#QA-RESULTS");
    await user.type(
      within(dialog).getByRole("textbox", { name: /^Webhook URL/ }),
      "http://hooks.slack.com/services/T0/B0/x",
    );
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(validation.nameAlreadyUsed)).toBeInTheDocument();
    expect(within(dialog).getByText(validation.urlNotHttps)).toBeInTheDocument();
    expect(within(dialog).getByText(validation.eventsRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("adds a Teams channel with the picked events", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [CHANNELS_PATH]: createCreatedResult(
        buildChatChannel({ id: "9d8c7b6a-5f4e-4d3c-8b2a-1f0e9d8c7b6a", name: "#ops" }),
      ),
    });
    renderCard();

    await user.click(await screen.findByRole("button", { name: card.add }));
    const dialog = await screen.findByRole("dialog");
    await user.click(await openSelectOption(user, /^Chat app/, kinds.teams));
    expect(within(dialog).getByText(new RegExp(form.teamsHelp.slice(0, 30)))).toBeInTheDocument();
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), " #ops ");
    await user.type(
      within(dialog).getByRole("textbox", { name: /^Webhook URL/ }),
      "https://example.webhook.office.com/workflows/abc",
    );
    await user.click(within(dialog).getByRole("checkbox", { name: events.gapRaised }));
    await user.click(within(dialog).getByRole("checkbox", { name: events.runStarted }));
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(CHANNELS_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          kind: "teams",
          name: "#ops",
          webhookUrl: "https://example.webhook.office.com/workflows/abc",
          events: ["run.started", "run.finished", "failure.opened", "gap.raised"],
          isActive: true,
        },
      });
    });
    expect(await screen.findByText(toasts.created)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
    expect(apiGet).toHaveBeenCalledTimes(2);
  });

  it("shows the server's URL refusal on the URL field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [CHANNELS_PATH]: createErrorResult(422, "WEBHOOK_URL_INVALID"),
    });
    renderCard();

    await user.click(await screen.findByRole("button", { name: card.add }));
    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), "#internal");
    await user.type(
      within(dialog).getByRole("textbox", { name: /^Webhook URL/ }),
      "https://10.0.0.5/hook",
    );
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(errors.urlInvalid)).toBeInTheDocument();
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("edits a channel without showing or resending its URL", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [CHANNEL_PATH]: (): ApiResult => {
        return createSuccessResult({
          ...results,
          ...(lastBody(apiPatch) as Partial<ChatChannel>),
        });
      },
    });
    renderCard();

    await openRowMenu(user, "#qa-results");
    await user.click(await screen.findByRole("menuitem", { name: card.edit }));
    const dialog = await screen.findByRole("dialog", { name: form.editTitle });
    expect(within(dialog).getByRole("textbox", { name: /^New webhook URL/ })).toHaveValue("");
    expect(
      within(dialog).getByText(/Saved URL: https:\/\/hooks\.slack\.com\/…9876/),
    ).toBeInTheDocument();
    expect(within(dialog).getByRole("checkbox", { name: events.runFinished })).toBeChecked();
    const nameInput = within(dialog).getByRole("textbox", { name: /^Name/ });
    await user.clear(nameInput);
    await user.type(nameInput, "#qa");
    await user.click(within(dialog).getByRole("checkbox", { name: events.planSignedOff }));
    await user.click(within(dialog).getByRole("button", { name: form.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(CHANNEL_PATH, {
        params: { path: { project_key: "SHOP", chat_channel_id: RESULTS_CHANNEL_ID } },
        body: { name: "#qa", events: ["run.finished", "failure.opened", "plan.signed_off"] },
      });
    });
    expect(await screen.findByText(toasts.updated)).toBeInTheDocument();
  });

  it("sends a test message", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [TEST_PATH]: createSuccessResult(results) });
    renderCard();

    await openRowMenu(user, "#qa-results");
    await user.click(await screen.findByRole("menuitem", { name: card.sendTest }));

    expect(
      await screen.findByText(toasts.testSent.replace("{{name}}", "#qa-results")),
    ).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith(TEST_PATH, {
      params: { path: { project_key: "SHOP", chat_channel_id: RESULTS_CHANNEL_ID } },
    });
    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledTimes(2);
    });
  });

  it("reports a test message that Slack or Teams refused and reloads the channel", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [TEST_PATH]: createErrorResult(502, "CHAT_DELIVERY_FAILED") });
    renderCard();

    await openRowMenu(user, "#releases");
    await user.click(await screen.findByRole("menuitem", { name: card.sendTest }));

    expect(
      await screen.findByText(toasts.testFailed.replace("{{name}}", "#releases")),
    ).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith(TEST_PATH, {
      params: { path: { project_key: "SHOP", chat_channel_id: RELEASES_CHANNEL_ID } },
    });
    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledTimes(2);
    });
  });

  it("turns a channel off", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [CHANNEL_PATH]: (): ApiResult => {
        return createSuccessResult({ ...results, isActive: false });
      },
    });
    renderCard();

    await openRowMenu(user, "#qa-results");
    await user.click(await screen.findByRole("menuitem", { name: card.turnOff }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(CHANNEL_PATH, {
        params: { path: { project_key: "SHOP", chat_channel_id: RESULTS_CHANNEL_ID } },
        body: { isActive: false },
      });
    });
    expect(
      await screen.findByText(toasts.turnedOff.replace("{{name}}", "#qa-results")),
    ).toBeInTheDocument();
  });

  it("offers to turn a channel that is off back on", async () => {
    const user = userEvent.setup();
    renderCard();

    await openRowMenu(user, "#releases");

    expect(await screen.findByRole("menuitem", { name: card.turnOn })).toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: card.turnOff })).toBeNull();
  });

  it("deletes a channel after asking", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiDelete, { [CHANNEL_PATH]: createNoContentResult() });
    renderCard();

    await openRowMenu(user, "#releases");
    await user.click(await screen.findByRole("menuitem", { name: card.delete }));
    const dialog = await screen.findByRole("dialog", { name: englishChatChannels.delete.title });
    expect(within(dialog).getByText(/Delete #releases\?/)).toBeInTheDocument();
    await user.click(
      within(dialog).getByRole("button", { name: englishChatChannels.delete.confirm }),
    );

    await waitFor(() => {
      expect(apiDelete).toHaveBeenCalledWith(CHANNEL_PATH, {
        params: { path: { project_key: "SHOP", chat_channel_id: RELEASES_CHANNEL_ID } },
      });
    });
    expect(await screen.findByText(toasts.deleted)).toBeInTheDocument();
  });

  it("stops adding channels at the project limit", async () => {
    const channels = Array.from({ length: 20 }, (_value, index) => {
      return buildChatChannel({
        id: `00000000-0000-4000-8000-${String(index).padStart(12, "0")}`,
        name: `#channel-${index}`,
      });
    });
    respondWithRoutes(apiGet, { [CHANNELS_PATH]: createSuccessResult(channels) });
    renderCard();

    expect(await screen.findByText(card.limitReached.replace("{{max}}", "20"))).toBeInTheDocument();
    expect(screen.getByRole("button", { name: card.add })).toBeDisabled();
  });
});
