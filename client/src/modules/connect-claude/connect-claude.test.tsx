import englishConnectClaude from "@/lib/i18n/locales/en/connectClaude.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
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
import { ConnectClaudePage } from "./connect-claude";
import { apiDelete, apiGet, apiPost } from "./test/mocks/api-client.mock";
import {
  createApiToken,
  createCreatedApiToken,
  createProject,
} from "./test/utils/api-token.fixture";
import type { ApiToken } from "./typing/types/api-token.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const SECRET_TOKEN = "tsio_a1b2c3d4_S3cretValue";
const TOKENS_PATH = "/api/me/api-tokens";

const ACTIVE_TOKEN = createApiToken({ id: "token-active", name: "Laptop" });
const EXPIRED_TOKEN = createApiToken({ id: "token-expired", name: "Old box", status: "expired" });
const REVOKED_TOKEN = createApiToken({
  id: "token-revoked",
  name: "Lost phone",
  status: "revoked",
  revokedAt: "2026-11-02T10:00:00Z",
  lastUsedAt: "2026-11-01T12:00:00Z",
});

const countTokenListCalls = (): number => {
  return apiGet.mock.calls.filter(([path]) => {
    return path === TOKENS_PATH;
  }).length;
};

const respondWithTokens = (tokens: ApiToken[], projects = [createProject()]): void => {
  respondWithRoutes(apiGet, {
    [TOKENS_PATH]: createSuccessResult(tokens),
    "/api/projects": createSuccessResult(projects),
  });
};

const fillCreateForm = async (projectLabel = "TES · Tessio"): Promise<void> => {
  const user = userEvent.setup();
  await user.type(
    await screen.findByRole("textbox", { name: englishConnectClaude.create.name }),
    "My laptop",
  );
  await user.click(screen.getByRole("combobox", { name: englishConnectClaude.create.project }));
  await user.click(await screen.findByRole("option", { name: projectLabel, hidden: true }));
};

const submitCreateForm = async (): Promise<void> => {
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name: englishConnectClaude.create.submit }));
};

describe("ConnectClaudePage", () => {
  beforeAll(() => {
    stubBrowserApis();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiDelete.mockReset();
    respondWithTokens([ACTIVE_TOKEN, EXPIRED_TOKEN, REVOKED_TOKEN]);
  });

  it("lists tokens with their status and offers Revoke only for active ones", async () => {
    const { container } = renderWithProviders(<ConnectClaudePage />);

    const table = await screen.findByRole("table");
    expect(within(table).getByText(englishConnectClaude.status.active)).toBeInTheDocument();
    expect(within(table).getByText(englishConnectClaude.status.expired)).toBeInTheDocument();
    expect(within(table).getByText(englishConnectClaude.status.revoked)).toBeInTheDocument();
    expect(within(table).getAllByText("tsio_a1b2c3d4_…")).toHaveLength(3);
    expect(within(table).getAllByText(englishConnectClaude.table.never)).toHaveLength(2);
    expect(screen.getByText("1 of 10 active")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Revoke Laptop" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Revoke Old box" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Revoke Lost phone" })).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("creates a token, shows it once inside the install command and forgets it on Done", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [TOKENS_PATH]: createSuccessResult(createCreatedApiToken(SECRET_TOKEN)),
    });
    const { queryClient } = renderWithProviders(<ConnectClaudePage />);

    await fillCreateForm();
    await submitCreateForm();

    expect(apiPost).toHaveBeenCalledWith(TOKENS_PATH, {
      body: { name: "My laptop", projectKey: "TES", expiresInDays: 30, scope: "mcp" },
    });
    const dialog = await screen.findByRole("dialog", { name: "Token for TES" });
    const command = `claude plugin install tessio --marketplace ${window.location.origin}/api/plugin/marketplace.json --config tessio_url=${window.location.origin} --config tessio_token=${SECRET_TOKEN}`;
    expect(within(dialog).getByText(command)).toBeInTheDocument();
    expect(within(dialog).getByText(SECRET_TOKEN)).toBeInTheDocument();
    expect(within(dialog).getAllByRole("button", { name: "Copy" })).toHaveLength(2);
    expect(within(dialog).getByText(englishConnectClaude.created.httpsOnly)).toBeInTheDocument();
    expect(await axe(dialog)).toHaveNoViolations();
    await waitFor(() => {
      expect(countTokenListCalls()).toBe(2);
    });
    expect(
      JSON.stringify(
        queryClient
          .getQueryCache()
          .getAll()
          .map((query) => query.state.data),
      ),
    ).not.toContain(SECRET_TOKEN);

    await user.click(
      within(dialog).getByRole("button", { name: englishConnectClaude.created.done }),
    );

    await waitFor(() => {
      expect(screen.queryByText(SECRET_TOKEN)).not.toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        JSON.stringify(
          queryClient
            .getMutationCache()
            .getAll()
            .map((mutation) => mutation.state.data),
        ),
      ).not.toContain(SECRET_TOKEN);
    });
    expect(screen.getByRole("textbox", { name: englishConnectClaude.create.name })).toHaveValue("");
  });

  it("shows the token limit error inline", async () => {
    respondWithRoutes(apiPost, { [TOKENS_PATH]: createErrorResult(409, "TOKEN_LIMIT_REACHED") });
    renderWithProviders(<ConnectClaudePage />);

    await fillCreateForm();
    await submitCreateForm();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishErrors.api.TOKEN_LIMIT_REACHED,
    );
  });

  it("shows a non-member error inline", async () => {
    respondWithRoutes(apiPost, { [TOKENS_PATH]: createErrorResult(403, "PERMISSION_DENIED") });
    renderWithProviders(<ConnectClaudePage />);

    await fillCreateForm();
    await submitCreateForm();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishConnectClaude.errors.notMember,
    );
  });

  it("blocks creation at 10 active tokens", async () => {
    const tokens = Array.from({ length: 10 }, (_value, index) => {
      return createApiToken({ id: `token-${index}`, name: `Token ${index}` });
    });
    respondWithTokens(tokens);
    renderWithProviders(<ConnectClaudePage />);

    expect(await screen.findByText(englishConnectClaude.create.limitReached)).toBeInTheDocument();
    expect(await screen.findByText("10 of 10 active")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishConnectClaude.create.submit })).toBeDisabled();
  });

  it("revokes an active token after confirmation and refetches the list", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiDelete, {
      "/api/me/api-tokens/{token_id}": createNoContentResult(),
    });
    renderWithProviders(<ConnectClaudePage />);

    await user.click(await screen.findByRole("button", { name: "Revoke Laptop" }));
    const dialog = await screen.findByRole("dialog", {
      name: englishConnectClaude.revoke.title,
    });
    expect(dialog).toHaveTextContent('Claude stops working with "Laptop" in TES at once.');
    await user.click(
      within(dialog).getByRole("button", { name: englishConnectClaude.revoke.confirm }),
    );

    expect(apiDelete).toHaveBeenCalledWith("/api/me/api-tokens/{token_id}", {
      params: { path: { token_id: "token-active" } },
    });
    await waitFor(() => {
      expect(countTokenListCalls()).toBe(2);
    });
    expect(await screen.findByText(englishConnectClaude.revoke.done)).toBeInTheDocument();
  });

  it("explains that a Viewer token cannot record results", async () => {
    respondWithTokens([], [createProject({ key: "VIE", name: "Viewing", myRole: "viewer" })]);
    renderWithProviders(<ConnectClaudePage />);

    await fillCreateForm("VIE · Viewing");

    expect(screen.getByText(englishConnectClaude.create.viewerHint)).toBeInTheDocument();
  });

  it("creates a REST API token for CI and shows the JUnit import call instead of the plugin", async () => {
    const user = userEvent.setup();
    const created = createCreatedApiToken(SECRET_TOKEN);
    respondWithRoutes(apiPost, {
      [TOKENS_PATH]: createSuccessResult({
        ...created,
        apiToken: { ...created.apiToken, scope: "api" },
      }),
    });
    renderWithProviders(<ConnectClaudePage />);

    await fillCreateForm();
    await user.click(screen.getByRole("combobox", { name: englishConnectClaude.scope.label }));
    await user.click(
      await screen.findByRole("option", {
        name: englishConnectClaude.scope.options.api,
        hidden: true,
      }),
    );
    expect(screen.getByText(englishConnectClaude.scope.descriptions.api)).toBeInTheDocument();
    await submitCreateForm();

    expect(apiPost).toHaveBeenCalledWith(TOKENS_PATH, {
      body: { name: "My laptop", projectKey: "TES", expiresInDays: 30, scope: "api" },
    });
    const dialog = await screen.findByRole("dialog", { name: "Token for TES" });
    const command = [
      `curl -X POST ${window.location.origin}/api/projects/TES/runs/import \\`,
      `  -H 'Authorization: Bearer ${SECRET_TOKEN}' \\`,
      "  -F file=@results.xml \\",
      "  -F environment=Staging",
    ].join("\n");
    expect(
      within(dialog).getByText((_, element) => {
        return element?.tagName === "PRE" && element.textContent === command;
      }),
    ).toBeInTheDocument();
    expect(within(dialog).getByText(englishConnectClaude.created.apiHint)).toBeInTheDocument();
    expect(within(dialog).queryByText(/claude plugin install/)).not.toBeInTheDocument();
    expect(
      within(dialog).queryByText(englishConnectClaude.created.httpsOnly),
    ).not.toBeInTheDocument();
    expect(await axe(dialog)).toHaveNoViolations();
  });

  it("shows what each token is used for in the list", async () => {
    respondWithTokens([
      createApiToken({ id: "token-mcp", name: "Laptop" }),
      createApiToken({ id: "token-api", name: "GitHub Actions", scope: "api" }),
    ]);
    renderWithProviders(<ConnectClaudePage />);

    const table = await screen.findByRole("table");
    const rows = within(table).getAllByRole("row");
    expect(within(rows[0]).getByText(englishConnectClaude.table.scope)).toBeInTheDocument();
    expect(within(rows[1]).getByText(englishConnectClaude.scope.short.mcp)).toBeInTheDocument();
    expect(within(rows[2]).getByText(englishConnectClaude.scope.short.api)).toBeInTheDocument();
  });

  it("explains that a Viewer REST API token can read but not import", async () => {
    const user = userEvent.setup();
    respondWithTokens([], [createProject({ key: "VIE", name: "Viewing", myRole: "viewer" })]);
    renderWithProviders(<ConnectClaudePage />);

    await fillCreateForm("VIE · Viewing");
    await user.click(screen.getByRole("combobox", { name: englishConnectClaude.scope.label }));
    await user.click(
      await screen.findByRole("option", {
        name: englishConnectClaude.scope.options.api,
        hidden: true,
      }),
    );

    expect(screen.getByText(englishConnectClaude.create.viewerApiHint)).toBeInTheDocument();
  });

  it("shows an empty state when the user has no projects", async () => {
    respondWithTokens([], []);
    const { container } = renderWithProviders(<ConnectClaudePage />);

    expect(await screen.findByText(englishConnectClaude.create.noProjects)).toBeInTheDocument();
    expect(screen.getByText(englishConnectClaude.table.empty)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: englishConnectClaude.create.submit }),
    ).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows an error state with retry when the tokens cannot load", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [TOKENS_PATH]: createErrorResult(500, "CONFLICT"),
      "/api/projects": createSuccessResult([createProject()]),
    });
    renderWithProviders(<ConnectClaudePage />);

    await user.click(await screen.findByRole("button", { name: englishConnectClaude.table.retry }));

    await waitFor(() => {
      expect(countTokenListCalls()).toBe(2);
    });
    expect(screen.getByText(englishConnectClaude.table.loadFailed)).toBeInTheDocument();
  });
});
