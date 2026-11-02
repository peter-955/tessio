import englishSuites from "@/lib/i18n/locales/en/suites.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SuitesPage } from "./suites";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerPush } from "./test/mocks/next-navigation.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { QC_PROJECT, VIEWER_PROJECT } from "./test/utils/suite-project.util";
import {
  ARCHIVED_SUITE_ID,
  RUN_ID,
  SUITE_ID,
  buildSuiteDetail,
  buildSuiteSummary,
} from "./test/utils/suite.fixture";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, boolean> };
}

const SUITES_PATH = "/api/projects/{project_key}/suites";

const { list, form, errors, toasts } = englishSuites;

const ACTIVE_SUITE = buildSuiteSummary({
  lastRun: {
    id: RUN_ID,
    status: "failed",
    startedAt: "2026-10-28T10:00:00Z",
    finishedAt: "2026-10-28T10:20:00Z",
  },
});

const ARCHIVED_SUITE = buildSuiteSummary({
  id: ARCHIVED_SUITE_ID,
  name: "Old smoke",
  description: null,
  caseCount: 1,
  readyCaseCount: 1,
  archivedAt: "2026-10-25T09:00:00Z",
});

const readListQueries = (): Record<string, boolean>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === SUITES_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

describe("SuitesPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    routerPush.mockReset();
    apiGet.mockImplementation((path, options) => {
      if (path !== SUITES_PATH) {
        return Promise.reject(new Error(`No mocked response for ${path}`));
      }

      const isArchivedShown = (options as ListRequest).params.query.archived === true;

      return Promise.resolve(
        createSuccessResult(isArchivedShown ? [ACTIVE_SUITE, ARCHIVED_SUITE] : [ACTIVE_SUITE]),
      );
    });
  });

  it("lists the suites with their case counts and last run", async () => {
    const { container } = renderWithProject(<SuitesPage />, QC_PROJECT);

    const table = await screen.findByRole("table", { name: list.tableLabel });
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(2);
    expect(within(rows[1]).getByRole("link", { name: "Checkout regression" })).toHaveAttribute(
      "href",
      `/projects/SHOP/suites/${SUITE_ID}`,
    );
    expect(within(rows[1]).getByText("3 cases")).toBeInTheDocument();
    expect(within(rows[1]).getByText("2 ready to run")).toBeInTheDocument();
    expect(within(rows[1]).getByText("Failed")).toBeInTheDocument();
    expect(within(rows[1]).getByRole("link", { name: /Oct 28/ })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs/${RUN_ID}`,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("adds the archived suites when asked", async () => {
    const user = userEvent.setup();
    renderWithProject(<SuitesPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Checkout regression" });

    await user.click(screen.getByRole("switch", { name: list.showArchived }));

    expect(await screen.findByRole("link", { name: "Old smoke" })).toBeInTheDocument();
    expect(screen.getByText(list.archived)).toBeInTheDocument();
    expect(readListQueries()).toEqual([{}, { archived: true }]);
  });

  it("shows the empty state with a create button for a QC", async () => {
    respondWithRoutes(apiGet, { [SUITES_PATH]: createSuccessResult([]) });
    renderWithProject(<SuitesPage />, QC_PROJECT);

    expect(await screen.findByText(list.emptyTitle)).toBeInTheDocument();
    expect(screen.getByText(list.emptyDescription)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: list.newSuite })).toHaveLength(2);
  });

  it("hides the create button from a viewer", async () => {
    respondWithRoutes(apiGet, { [SUITES_PATH]: createSuccessResult([]) });
    renderWithProject(<SuitesPage />, VIEWER_PROJECT);

    expect(await screen.findByText(list.emptyReadOnlyDescription)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: list.newSuite })).toBeNull();
  });

  it("hides the create button in an archived project", async () => {
    renderWithProject(<SuitesPage />, { ...QC_PROJECT, isArchived: true });

    await screen.findByRole("link", { name: "Checkout regression" });
    expect(screen.queryByRole("button", { name: list.newSuite })).toBeNull();
  });

  it("shows an error with a retry when the list fails", async () => {
    respondWithRoutes(apiGet, { [SUITES_PATH]: createErrorResult(500, "CONFLICT") });
    renderWithProject(<SuitesPage />, QC_PROJECT);

    expect(await screen.findByText(list.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: list.retry })).toBeInTheDocument();
  });

  it("creates a suite with a trimmed name and opens it", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [SUITES_PATH]: createSuccessResult(buildSuiteDetail()) });
    renderWithProject(<SuitesPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Checkout regression" });

    await user.click(screen.getByRole("button", { name: list.newSuite }));
    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), "  Smoke  ");
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(SUITES_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: { name: "Smoke", description: null },
      });
    });
    expect(await screen.findByText(toasts.created)).toBeInTheDocument();
    expect(routerPush).toHaveBeenCalledWith(`/projects/SHOP/suites/${SUITE_ID}`);
  });

  it("asks for a name before it creates a suite", async () => {
    const user = userEvent.setup();
    renderWithProject(<SuitesPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Checkout regression" });

    await user.click(screen.getByRole("button", { name: list.newSuite }));
    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(form.nameRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows the server's name conflict on the name field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [SUITES_PATH]: createErrorResult(409, "SUITE_NAME_ALREADY_USED"),
    });
    renderWithProject(<SuitesPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Checkout regression" });

    await user.click(screen.getByRole("button", { name: list.newSuite }));
    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), "checkout regression");
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(errors.nameAlreadyUsed)).toBeVisible();
    expect(routerPush).not.toHaveBeenCalled();
  });
});
