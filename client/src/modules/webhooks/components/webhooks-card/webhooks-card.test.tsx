import { ProjectContext } from "@/components/project-context/contexts/project.context";
import englishIntegrations from "@/lib/i18n/locales/en/integrations.json";
import {
  createErrorResult,
  createNoContentResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { stubBrowserApis } from "@/modules/projects/test/utils/stub-browser-apis.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiDelete, apiGet, apiPatch, apiPost } from "../../test/mocks/api-client.mock";
import {
  DELIVERY_ID,
  WEBHOOK_ID,
  WEBHOOK_SECRET,
  buildIntegrationAdminProject,
  buildWebhook,
  buildWebhookDelivery,
} from "../../test/utils/webhook.fixture";
import type { Webhook } from "../../typing/types/webhook.type";
import { WebhooksCard } from "./webhooks-card";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const WEBHOOKS_PATH = "/api/projects/{project_key}/webhooks";
const WEBHOOK_PATH = "/api/projects/{project_key}/webhooks/{webhook_id}";
const DELIVERIES_PATH = "/api/projects/{project_key}/webhooks/{webhook_id}/deliveries";
const REDELIVER_PATH = "/api/projects/{project_key}/webhooks/{webhook_id}/redeliver/{delivery_id}";

const { webhooks, form, errors, secret, rotate, deliveries, events } = englishIntegrations;

const respondWithWebhooks = (list: Webhook[]): void => {
  respondWithRoutes(apiGet, {
    [WEBHOOKS_PATH]: createSuccessResult(list),
    [DELIVERIES_PATH]: createSuccessResult([
      buildWebhookDelivery(),
      buildWebhookDelivery({
        id: "7c000000-0000-4000-8000-000000000002",
        event: "run.started",
        status: "succeeded",
        attempts: 1,
        responseStatus: 200,
        error: null,
        deliveredAt: "2026-11-02T10:00:01Z",
      }),
    ]),
  });
};

const renderCard = () => {
  return renderWithProviders(
    <ProjectContext value={buildIntegrationAdminProject()}>
      <WebhooksCard projectKey="SHOP" />
    </ProjectContext>,
  );
};

const findWebhookRow = async (): Promise<HTMLElement> => {
  const table = await screen.findByRole("table");

  return within(table).getAllByRole("row")[1];
};

const openMenuItem = async (itemName: string): Promise<void> => {
  const user = userEvent.setup();
  await user.click(
    await screen.findByRole("button", {
      name: `Actions for ${buildWebhook().url}`,
    }),
  );
  await user.click(await screen.findByRole("menuitem", { name: itemName }));
};

describe("WebhooksCard", () => {
  beforeAll(() => {
    stubBrowserApis();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPatch.mockReset();
    apiDelete.mockReset();
    respondWithWebhooks([
      buildWebhook(),
      buildWebhook({
        id: "7b000000-0000-4000-8000-000000000002",
        url: "https://bots.example.com/tessio",
        description: null,
        events: [
          "run.started",
          "run.finished",
          "failure.opened",
          "failure.status_changed",
          "gap.raised",
          "story.signed_off",
          "plan.signed_off",
        ],
        isActive: false,
        lastDelivery: null,
      }),
    ]);
  });

  it("lists each webhook with its events, status, secret hint and last delivery", async () => {
    const { container } = renderCard();

    const row = within(await findWebhookRow());
    expect(row.getByText("https://ci.example.com/hooks/tessio")).toBeInTheDocument();
    expect(row.getByText("Release dashboard")).toBeInTheDocument();
    expect(row.getByText("Secret whsec_…a1b2")).toBeInTheDocument();
    expect(row.getByText(`${events.runStarted}, ${events.runFinished}`)).toBeInTheDocument();
    expect(row.getByText(webhooks.active)).toBeInTheDocument();
    expect(row.getByText(deliveries.status.failed)).toBeInTheDocument();

    const secondRow = within(within(screen.getByRole("table")).getAllByRole("row")[2]);
    expect(secondRow.getByText(webhooks.allEvents)).toBeInTheDocument();
    expect(secondRow.getByText(webhooks.inactive)).toBeInTheDocument();
    expect(secondRow.getByText(webhooks.noDelivery)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows an empty text without webhooks and an error state with retry", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { [WEBHOOKS_PATH]: createErrorResult(500, "INVALID_REQUEST") });
    renderCard();

    expect(await screen.findByText(webhooks.loadError)).toBeInTheDocument();
    respondWithWebhooks([]);
    await user.click(screen.getByRole("button", { name: webhooks.retry }));

    expect(await screen.findByText(webhooks.empty)).toBeInTheDocument();
  });

  it("checks the form, adds a webhook and shows its secret once", async () => {
    const user = userEvent.setup();
    const created = buildWebhook({ url: "https://hooks.example.com/tessio", lastDelivery: null });
    respondWithRoutes(apiPost, {
      [WEBHOOKS_PATH]: createSuccessResult({ webhook: created, secret: WEBHOOK_SECRET }),
    });
    renderCard();

    await user.click(await screen.findByRole("button", { name: webhooks.add }));
    const dialog = await screen.findByRole("dialog", { name: form.createTitle });
    const urlInput = within(dialog).getByRole("textbox", { name: new RegExp(form.url) });
    await user.type(urlInput, "http://hooks.example.com/tessio");
    for (const label of Object.values(events)) {
      await user.click(within(dialog).getByRole("checkbox", { name: new RegExp(label) }));
    }
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(errors.urlNotHttps)).toBeInTheDocument();
    expect(within(dialog).getByText(errors.eventsRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();

    await user.clear(urlInput);
    await user.type(urlInput, "https://hooks.example.com/tessio");
    await user.click(within(dialog).getByRole("checkbox", { name: new RegExp(events.gapRaised) }));
    await user.click(within(dialog).getByRole("checkbox", { name: new RegExp(events.runStarted) }));
    await user.type(within(dialog).getByRole("textbox", { name: form.description }), "Release bot");
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(WEBHOOKS_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          url: "https://hooks.example.com/tessio",
          description: "Release bot",
          events: ["run.started", "gap.raised"],
          isActive: true,
        },
      });
    });
    const secretDialog = await screen.findByRole("dialog", { name: secret.title });
    expect(within(secretDialog).getByText(WEBHOOK_SECRET)).toBeInTheDocument();
    expect(within(secretDialog).getByText(secret.shownOnce)).toBeInTheDocument();
    expect(await axe(secretDialog)).toHaveNoViolations();

    await user.click(within(secretDialog).getByRole("button", { name: secret.done }));
    await waitFor(() => {
      expect(screen.queryByText(WEBHOOK_SECRET)).not.toBeInTheDocument();
    });
  });

  it("shows a refused URL on the URL field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [WEBHOOKS_PATH]: createErrorResult(422, "WEBHOOK_URL_INVALID"),
    });
    renderCard();

    await user.click(await screen.findByRole("button", { name: webhooks.add }));
    const dialog = await screen.findByRole("dialog", { name: form.createTitle });
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(form.url) }),
      "https://10.0.0.1.nip.io/hook",
    );
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(errors.urlInvalid)).toBeInTheDocument();
  });

  it("saves only the changed fields of a webhook", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [WEBHOOK_PATH]: createSuccessResult({ webhook: buildWebhook(), secret: null }),
    });
    renderCard();

    await openMenuItem(webhooks.menu.edit);
    const dialog = await screen.findByRole("dialog", { name: form.editTitle });
    await user.click(within(dialog).getByRole("switch", { name: new RegExp(form.isActive) }));
    await user.click(within(dialog).getByRole("button", { name: form.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(WEBHOOK_PATH, {
        params: { path: { project_key: "SHOP", webhook_id: WEBHOOK_ID } },
        body: { rotateSecret: false, isActive: false },
      });
    });
  });

  it("rotates the secret after confirmation and shows the new one", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [WEBHOOK_PATH]: createSuccessResult({ webhook: buildWebhook(), secret: WEBHOOK_SECRET }),
    });
    renderCard();

    await openMenuItem(webhooks.menu.rotate);
    const dialog = await screen.findByRole("dialog", { name: rotate.title });
    await user.click(within(dialog).getByRole("button", { name: rotate.confirm }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(WEBHOOK_PATH, {
        params: { path: { project_key: "SHOP", webhook_id: WEBHOOK_ID } },
        body: { rotateSecret: true },
      });
    });
    const secretDialog = await screen.findByRole("dialog", { name: secret.title });
    expect(within(secretDialog).getByText(WEBHOOK_SECRET)).toBeInTheDocument();
  });

  it("removes a webhook after confirmation", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiDelete, { [WEBHOOK_PATH]: createNoContentResult() });
    renderCard();

    await openMenuItem(webhooks.menu.delete);
    const dialog = await screen.findByRole("dialog", { name: englishIntegrations.delete.title });
    await user.click(
      within(dialog).getByRole("button", { name: englishIntegrations.delete.confirm }),
    );

    await waitFor(() => {
      expect(apiDelete).toHaveBeenCalledWith(WEBHOOK_PATH, {
        params: { path: { project_key: "SHOP", webhook_id: WEBHOOK_ID } },
      });
    });
  });

  it("shows the delivery log with the payload and redelivers a delivery", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [REDELIVER_PATH]: createSuccessResult(
        buildWebhookDelivery({ id: "7c000000-0000-4000-8000-000000000003", status: "pending" }),
      ),
    });
    renderCard();

    await openMenuItem(webhooks.menu.deliveries);
    const drawer = await screen.findByRole("dialog", { name: deliveries.title });
    const table = await within(drawer).findByRole("table");
    const failedRow = within(within(table).getAllByRole("row")[1]);
    expect(failedRow.getByText(events.runFinished)).toBeInTheDocument();
    expect(failedRow.getByText(deliveries.status.failed)).toBeInTheDocument();
    expect(failedRow.getByText("5 tries")).toBeInTheDocument();
    expect(failedRow.getByText("The receiver answered HTTP 500.")).toBeInTheDocument();
    const deliveredRow = within(within(table).getAllByRole("row")[2]);
    expect(deliveredRow.getByText(deliveries.status.succeeded)).toBeInTheDocument();
    expect(deliveredRow.getByText("1 try")).toBeInTheDocument();
    expect(apiGet).toHaveBeenCalledWith(DELIVERIES_PATH, {
      params: { path: { project_key: "SHOP", webhook_id: WEBHOOK_ID }, query: { limit: 50 } },
      signal: expect.any(AbortSignal) as AbortSignal,
    });

    await user.click(failedRow.getByRole("button", { name: /^Show the payload of Run finished/ }));
    expect(await within(drawer).findByText(/"event": "run.finished"/)).toBeInTheDocument();
    expect(await axe(drawer)).toHaveNoViolations();

    await user.click(failedRow.getByRole("button", { name: /^Redeliver Run finished/ }));
    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(REDELIVER_PATH, {
        params: {
          path: { project_key: "SHOP", webhook_id: WEBHOOK_ID, delivery_id: DELIVERY_ID },
        },
      });
    });
  });

  it("stops adding webhooks at 20 per project", async () => {
    respondWithWebhooks(
      Array.from({ length: 20 }, (_, index) => {
        return buildWebhook({
          id: `7b000000-0000-4000-8000-${String(index).padStart(12, "0")}`,
          url: `https://ci.example.com/hooks/${String(index)}`,
        });
      }),
    );
    renderCard();

    expect(await screen.findByText(errors.limitReached)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: webhooks.add })).toBeDisabled();
  });
});
