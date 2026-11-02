import englishSharedSteps from "@/lib/i18n/locales/en/sharedSteps.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SharedStepsPage } from "./shared-steps";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerPush } from "./test/mocks/next-navigation.mock";
import { interpolate } from "./test/utils/interpolate.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { QC_PROJECT, VIEWER_PROJECT } from "./test/utils/shared-step-project.util";
import { ARCHIVED_SHARED_STEP, buildSharedStep } from "./test/utils/shared-step.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, boolean> };
}

interface CreateRequest {
  body: unknown;
}

const SHARED_STEPS_PATH = "/api/projects/{project_key}/shared-steps";
const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";

const { list, usage, form, errors, toasts } = englishSharedSteps;

const ACTIVE_STEP = buildSharedStep();

const readListQueries = (): Record<string, boolean>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === SHARED_STEPS_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

describe("SharedStepsPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    routerPush.mockReset();
    apiGet.mockImplementation((path, options) => {
      if (path === TEST_DATA_PATH) {
        return Promise.resolve(createSuccessResult([]));
      }

      if (path !== SHARED_STEPS_PATH) {
        return Promise.reject(new Error(`No mocked response for ${path}`));
      }

      const isArchivedShown = (options as ListRequest).params.query.archived === true;

      return Promise.resolve(
        createSuccessResult(isArchivedShown ? [ACTIVE_STEP, ARCHIVED_SHARED_STEP] : [ACTIVE_STEP]),
      );
    });
  });

  it("lists the shared steps with how many cases use each one", async () => {
    const { container } = renderWithProject(<SharedStepsPage />, QC_PROJECT);

    const table = await screen.findByRole("table", { name: list.tableLabel });
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(2);
    expect(within(rows[1]).getByRole("link", { name: "Log in as admin" })).toHaveAttribute(
      "href",
      "/projects/SHOP/shared-steps/login_as_admin",
    );
    expect(within(rows[1]).getByText("login_as_admin")).toBeInTheDocument();
    expect(within(rows[1]).getByText("2 steps")).toBeInTheDocument();
    expect(
      within(rows[1]).getByText(interpolate(usage.count_other, { count: 3 })),
    ).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("adds the archived shared steps when asked", async () => {
    const user = userEvent.setup();
    renderWithProject(<SharedStepsPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Log in as admin" });

    await user.click(screen.getByRole("switch", { name: list.showArchived }));

    expect(await screen.findByRole("link", { name: "Old login" })).toBeInTheDocument();
    expect(screen.getByText(list.archived)).toBeInTheDocument();
    expect(screen.getByText(interpolate(usage.count_one, { count: 1 }))).toBeInTheDocument();
    expect(readListQueries()).toEqual([{}, { archived: true }]);
  });

  it("shows an empty state and hides New for a viewer", async () => {
    respondWithRoutes(apiGet, { [SHARED_STEPS_PATH]: createSuccessResult([]) });
    renderWithProject(<SharedStepsPage />, VIEWER_PROJECT);

    expect(await screen.findByText(list.emptyTitle)).toBeInTheDocument();
    expect(screen.getByText(list.emptyReadOnlyDescription)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: list.newSharedStep })).not.toBeInTheDocument();
  });

  it("shows an error with a retry when the list fails", async () => {
    respondWithRoutes(apiGet, { [SHARED_STEPS_PATH]: createErrorResult(500, "INVALID_REQUEST") });
    renderWithProject(<SharedStepsPage />, QC_PROJECT);

    expect(await screen.findByText(list.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: list.retry })).toBeInTheDocument();
  });

  it("creates a shared step with a lowercased key and opens it", async () => {
    const user = userEvent.setup();
    const created = buildSharedStep({ key: "login_as_qc", title: "Log in as QC", usageCount: 0 });
    respondWithRoutes(apiPost, { [SHARED_STEPS_PATH]: createSuccessResult(created) });
    renderWithProject(<SharedStepsPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Log in as admin" });

    await user.click(screen.getByRole("button", { name: list.newSharedStep }));
    const dialog = await screen.findByRole("dialog", { name: form.createTitle });
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${form.title}`) }),
      "Log in as QC",
    );
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${form.key}`) }),
      " Login_As_QC ",
    );
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${form.action}`) }),
      "Sign in as the QC user",
    );
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(SHARED_STEPS_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          key: "login_as_qc",
          title: "Log in as QC",
          steps: [{ action: "Sign in as the QC user", expected: null }],
        },
      });
    });
    expect(
      await screen.findByText(interpolate(toasts.created, { title: "Log in as QC" })),
    ).toBeInTheDocument();
    expect(routerPush).toHaveBeenCalledWith("/projects/SHOP/shared-steps/login_as_qc");
  });

  it("checks the form before sending and shows a key already used on the key field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [SHARED_STEPS_PATH]: createErrorResult(409, "SHARED_STEP_KEY_ALREADY_USED"),
    });
    renderWithProject(<SharedStepsPage />, QC_PROJECT);
    await screen.findByRole("link", { name: "Log in as admin" });

    await user.click(screen.getByRole("button", { name: list.newSharedStep }));
    const dialog = await screen.findByRole("dialog", { name: form.createTitle });
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${form.key}`) }),
      "1-bad",
    );
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(within(dialog).getByText(form.errors.invalidKey)).toBeInTheDocument();
    expect(within(dialog).getAllByText(form.errors.required).length).toBeGreaterThan(0);
    expect(apiPost).not.toHaveBeenCalled();

    const keyField = within(dialog).getByRole("textbox", { name: new RegExp(`^${form.key}`) });
    await user.clear(keyField);
    await user.type(keyField, "login_as_admin");
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${form.title}`) }),
      "Duplicate",
    );
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${form.action}`) }),
      "Sign in",
    );
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    expect(await within(dialog).findByText(errors.keyAlreadyUsed)).toBeInTheDocument();
    expect(
      (
        (apiPost.mock.calls[0] as [string, CreateRequest] | undefined)?.[1].body as {
          key: string;
        }
      ).key,
    ).toBe("login_as_admin");
  });
});
