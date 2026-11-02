import englishDataRows from "@/lib/i18n/locales/en/dataRows.json";
import englishSharedSteps from "@/lib/i18n/locales/en/sharedSteps.json";
import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import {
  buildSharedStep,
  buildSharedStepVersion,
} from "@/modules/shared-steps/test/utils/shared-step.fixture";
import { buildDataItem } from "@/modules/test-data/test/utils/test-data-fixture.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { CaseReadView } from "./components/case-read-view/case-read-view";
import { NewTestCasePage } from "./new-test-case";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { interpolate } from "./test/utils/interpolate.util";
import { buildProject, QC_CAPABILITIES } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import {
  buildStoryDetail,
  buildStorySummary,
  buildTestCaseDetail,
  buildTestCaseVersion,
} from "./test/utils/test-case-fixture.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const CREATE_PATH = "/api/projects/{project_key}/test-cases";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";
const SHARED_STEPS_PATH = "/api/projects/{project_key}/shared-steps";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const EFFECTIVE_TEST_DATA_PATH = "/api/projects/{project_key}/test-data/effective";

const { actions, form } = englishTestCases;
const { picker, reference } = englishSharedSteps;
const { editor, table, iteration } = englishDataRows;

const LOGIN_STEP = buildSharedStep();

const ARCHIVED_STEP = buildSharedStep({
  id: "e1000000-0000-4000-8000-000000000003",
  key: "old_login",
  title: "Old login",
  isArchived: true,
  archivedAt: "2026-10-25T10:00:00Z",
  currentVersion: buildSharedStepVersion({
    steps: [{ order: 1, action: "Use the old login form", expected: null }],
  }),
});

describe("Shared steps and data rows in a test case", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    setNavigation("/projects/SHOP/test-cases/new");
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStorySummary()]),
      [STORY_PATH]: createSuccessResult(buildStoryDetail()),
      [TEST_DATA_PATH]: createSuccessResult([]),
      [SHARED_STEPS_PATH]: createSuccessResult([LOGIN_STEP, ARCHIVED_STEP]),
      [ENVIRONMENTS_PATH]: createSuccessResult([]),
      [EFFECTIVE_TEST_DATA_PATH]: createSuccessResult([]),
    });
    respondWithRoutes(apiPost, {
      [CREATE_PATH]: createCreatedResult(buildTestCaseDetail({ code: "TC-8" })),
    });
  });

  it("inserts a shared step shown collapsed, expands it read-only and saves the data rows", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProject(
      <NewTestCasePage initialStoryKey="SHOP-1" />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    await user.type(screen.getByRole("textbox", { name: new RegExp(`^${form.title}`) }), "Login");
    await user.type(
      screen.getByRole("textbox", { name: new RegExp(`^${form.action}`) }),
      "Open {{{{param.page}}",
    );

    await user.click(screen.getByRole("button", { name: picker.open }));
    const dialog = await screen.findByRole("dialog", { name: picker.title });
    const combobox = within(dialog).getByRole("combobox", {
      name: new RegExp(`^${picker.select}`),
    });
    await user.click(combobox);
    expect(screen.queryByRole("option", { name: /Old login/, hidden: true })).toBeNull();
    await user.click(
      await openSelectOption(
        user,
        new RegExp(`^${picker.select}`),
        "Log in as admin (login_as_admin)",
      ),
    );
    expect(within(dialog).getByText("Open the sign-in page")).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: picker.insert }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: picker.title })).not.toBeInTheDocument();
    });
    const insertedLink = await screen.findByRole("link", { name: "Log in as admin" });
    expect(insertedLink).toHaveAttribute("href", "/projects/SHOP/shared-steps/login_as_admin");
    expect(screen.getByText(interpolate(reference.stepCount_other, { count: "2" }))).toBeVisible();
    expect(screen.queryByText("Open the sign-in page")).not.toBeInTheDocument();
    const showButton = screen.getByRole("button", { name: reference.showSteps });
    expect(showButton).toHaveAttribute("aria-expanded", "false");

    await user.click(showButton);
    const sharedSteps = screen.getByRole("list", {
      name: interpolate(reference.stepsOf, { title: "Log in as admin" }),
    });
    expect(within(sharedSteps).getByText("Open the sign-in page")).toBeInTheDocument();
    expect(within(sharedSteps).queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: reference.hideSteps })).toHaveAttribute(
      "aria-expanded",
      "true",
    );

    expect(screen.getByRole("heading", { name: editor.title })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    await user.type(screen.getByRole("textbox", { name: "Parameter 1 name" }), "page");
    await user.click(screen.getByRole("button", { name: editor.addRow }));
    await user.type(screen.getByRole("textbox", { name: "Row 1, page" }), "/cart");
    await user.click(screen.getByRole("button", { name: editor.addRow }));
    await user.type(screen.getByRole("textbox", { name: "Row 2, page" }), "/orders");

    await user.click(screen.getByRole("button", { name: actions.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(CREATE_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          storyKey: "SHOP-1",
          title: "Login",
          priority: "medium",
          businessValue: null,
          preconditions: null,
          steps: [
            { action: "Open {{param.page}}", expected: null },
            { sharedStepKey: "login_as_admin" },
          ],
          criterionIds: [],
          parameters: ["page"],
          dataRows: [{ page: "/cart" }, { page: "/orders" }],
        },
      });
    });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the test data values, not the raw references, in an expanded shared step", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStorySummary()]),
      [STORY_PATH]: createSuccessResult(buildStoryDetail()),
      [TEST_DATA_PATH]: createSuccessResult([]),
      [SHARED_STEPS_PATH]: createSuccessResult([LOGIN_STEP]),
      [ENVIRONMENTS_PATH]: createSuccessResult([]),
      [EFFECTIVE_TEST_DATA_PATH]: createSuccessResult([
        buildDataItem({ key: "admin_email", value: "admin@shop.test" }),
      ]),
    });
    renderWithProject(
      <NewTestCasePage initialStoryKey="SHOP-1" />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    await user.click(screen.getByRole("button", { name: picker.open }));
    const dialog = await screen.findByRole("dialog", { name: picker.title });
    await user.click(
      await openSelectOption(
        user,
        new RegExp(`^${picker.select}`),
        "Log in as admin (login_as_admin)",
      ),
    );
    await user.click(within(dialog).getByRole("button", { name: picker.insert }));
    await user.click(await screen.findByRole("button", { name: reference.showSteps }));

    const sharedSteps = screen.getByRole("list", {
      name: interpolate(reference.stepsOf, { title: "Log in as admin" }),
    });
    expect(await within(sharedSteps).findByText("admin@shop.test")).toBeInTheDocument();
    expect(within(sharedSteps).queryByText(/\{\{data\.admin_email\}\}/)).toBeNull();
  });

  it("does not save parameters without a data row", async () => {
    const user = userEvent.setup();
    renderWithProject(
      <NewTestCasePage initialStoryKey="SHOP-1" />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    await user.type(screen.getByRole("textbox", { name: new RegExp(`^${form.title}`) }), "Login");
    await user.type(screen.getByRole("textbox", { name: new RegExp(`^${form.action}`) }), "Open");
    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    await user.type(screen.getByRole("textbox", { name: "Parameter 1 name" }), "page");
    await user.click(screen.getByRole("button", { name: actions.create }));

    expect(await screen.findByText(editor.errors.parametersWithoutRows)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("does not send a case whose parameters are invalid", async () => {
    const user = userEvent.setup();
    renderWithProject(
      <NewTestCasePage initialStoryKey="SHOP-1" />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    await user.type(screen.getByRole("textbox", { name: new RegExp(`^${form.title}`) }), "Login");
    await user.type(screen.getByRole("textbox", { name: new RegExp(`^${form.action}`) }), "Open");
    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    await user.type(screen.getByRole("textbox", { name: "Parameter 1 name" }), "page");
    await user.type(screen.getByRole("textbox", { name: "Parameter 2 name" }), "Page");
    await user.click(screen.getByRole("button", { name: actions.create }));

    expect(await screen.findAllByText(editor.errors.duplicateName)).toHaveLength(2);
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows shared steps and the data rows in the read view, archived steps included", async () => {
    const user = userEvent.setup();
    const detail = buildTestCaseDetail({
      currentVersion: buildTestCaseVersion({
        steps: [
          { order: 1, action: "Open {{param.page}}", expected: null, sharedStepKey: null },
          { order: 2, action: null, expected: null, sharedStepKey: "old_login" },
        ],
        parameters: ["page"],
        dataRows: [{ page: "/cart" }, { page: "/orders" }],
      }),
    });
    renderWithProject(
      <CaseReadView detail={detail} canEdit={false} onEdit={vi.fn()} />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    expect(await screen.findByRole("link", { name: "Old login" })).toBeInTheDocument();
    expect(screen.getByText(reference.archived)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: reference.showSteps }));
    expect(screen.getByText("Use the old login form")).toBeInTheDocument();

    expect(
      screen.getByRole("heading", { name: interpolate(table.title_other, { count: "2" }) }),
    ).toBeInTheDocument();
    const rows = within(screen.getByRole("table", { name: table.label })).getAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(within(rows[0] as HTMLElement).getByText(table.iteration)).toBeInTheDocument();
    expect(within(rows[2] as HTMLElement).getByText("/orders")).toBeInTheDocument();
    expect(screen.queryByText(iteration.recordHint)).not.toBeInTheDocument();
  });
});
