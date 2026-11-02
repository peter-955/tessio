import englishAiHarness from "@/lib/i18n/locales/en/aiHarness.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { createApiToken } from "@/modules/connect-claude/test/utils/api-token.fixture";
import type { ApiToken } from "@/modules/connect-claude/typing/types/api-token.type";
import { screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { AiHarnessPage } from "./ai-harness";
import { apiGet } from "./test/mocks/api-client.mock";
import { createAiHarness } from "./test/utils/ai-harness.fixture";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const HARNESS_PATH = "/api/ai-harness";
const TOKENS_PATH = "/api/me/api-tokens";

const respondWith = (tokens: ApiToken[], harness = createAiHarness()): void => {
  respondWithRoutes(apiGet, {
    [HARNESS_PATH]: createSuccessResult(harness),
    [TOKENS_PATH]: createSuccessResult(tokens),
  });
};

describe("AiHarnessPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
  });

  it("shows the versions, skills, hooks and MCP tools with the roles allowed", async () => {
    respondWith([createApiToken({ name: "Laptop", pluginVersion: "0.3.0" })]);
    const { container } = renderWithProviders(<AiHarnessPage />);

    expect(await screen.findByText("0.1.0")).toBeInTheDocument();
    expect(screen.getByText("commit 6792d1a")).toBeInTheDocument();
    const tokens = await screen.findByRole("region", {
      name: englishAiHarness.versions.yourPluginsLabel,
    });
    const laptopRow = within(tokens).getByRole("row", { name: /Laptop/ });
    expect(within(laptopRow).getByText(englishAiHarness.pluginState.current)).toBeInTheDocument();

    const skills = screen.getByRole("region", { name: englishAiHarness.skills.label });
    expect(
      within(skills).getByText("/tessio:run-story-tests <STORY-KEY> [environment] [case codes]"),
    ).toBeInTheDocument();
    expect(screen.getByText(englishAiHarness.commands.empty)).toBeInTheDocument();

    const hooks = screen.getByRole("region", { name: englishAiHarness.hooks.label });
    expect(within(hooks).getByText("record_case_result")).toBeInTheDocument();
    expect(within(hooks).getByText("hooks/upload_screenshots.py")).toBeInTheDocument();

    expect(screen.getByText("https://tessio.test/mcp")).toBeInTheDocument();
    const tools = screen.getByRole("region", { name: englishAiHarness.mcp.toolsLabel });
    const startRunRow = within(tools).getByRole("row", { name: /start_run/ });
    expect(within(startRunRow).getByText("run.start")).toBeInTheDocument();
    expect(within(startRunRow).getByText("QC")).toBeInTheDocument();
    expect(within(startRunRow).queryByText("Viewer")).not.toBeInTheDocument();
    expect(screen.queryByText(englishAiHarness.versions.updateTitle)).not.toBeInTheDocument();

    expect(await axe(container)).toHaveNoViolations();
  });

  it("marks an older plugin as out of date and shows the update command", async () => {
    respondWith([
      createApiToken({ id: "token-old", name: "Old laptop", pluginVersion: "0.2.0" }),
      createApiToken({ id: "token-new", name: "New laptop", pluginVersion: null }),
      createApiToken({ id: "token-revoked", name: "Lost phone", status: "revoked" }),
    ]);
    renderWithProviders(<AiHarnessPage />);

    const tokens = await screen.findByRole("region", {
      name: englishAiHarness.versions.yourPluginsLabel,
    });
    const oldRow = within(tokens).getByRole("row", { name: /Old laptop/ });
    expect(within(oldRow).getByText(englishAiHarness.pluginState.outdated)).toBeInTheDocument();
    const newRow = within(tokens).getByRole("row", { name: /New laptop/ });
    expect(within(newRow).getAllByText(englishAiHarness.pluginState.unused)).not.toHaveLength(0);
    expect(within(tokens).queryByText("Lost phone")).not.toBeInTheDocument();
    expect(screen.getByText(englishAiHarness.versions.updateTitle)).toBeInTheDocument();
    expect(
      screen.getByText(
        "claude plugin marketplace update tessio && claude plugin update tessio@tessio",
      ),
    ).toBeInTheDocument();
  });

  it("links to Connect Claude when the user has no active token", async () => {
    respondWith([]);
    renderWithProviders(<AiHarnessPage />);

    expect(await screen.findByText(englishAiHarness.versions.noTokens)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: englishAiHarness.versions.connect })).toHaveAttribute(
      "href",
      "/connect-claude",
    );
  });

  it("offers Retry when the harness cannot be loaded", async () => {
    respondWithRoutes(apiGet, {
      [HARNESS_PATH]: createErrorResult(500, "CONFLICT"),
      [TOKENS_PATH]: createSuccessResult([]),
    });
    renderWithProviders(<AiHarnessPage />);

    expect(await screen.findByText(englishAiHarness.loadFailed)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishAiHarness.retry })).toBeInTheDocument();
  });
});
