import englishSuites from "@/lib/i18n/locales/en/suites.json";
import { createSuccessResult, respondWithRoutes } from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPut } from "../../test/mocks/api-client.mock";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { QC_PROJECT } from "../../test/utils/suite-project.util";
import { CASE_IDS, SUITE_ID, buildSuiteDetail } from "../../test/utils/suite.fixture";
import { AddCasesModal } from "./add-cases-modal";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

interface ListRequest {
  params: { query: Record<string, string> };
}

const TEST_CASES_PATH = "/api/projects/{project_key}/test-cases";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const CASES_PATH = "/api/projects/{project_key}/suites/{suite_id}/cases";
const NEW_CASE_ID = "5d000000-0000-4000-8000-000000000009";

const { addCases } = englishSuites;

const PROJECT_CASES = [
  {
    id: CASE_IDS[0],
    code: "TC-1",
    title: "Pay with a valid card",
    storyKey: "SHOP-1",
    status: "ready",
  },
  { id: NEW_CASE_ID, code: "TC-9", title: "Pay in two parts", storyKey: "SHOP-3", status: "draft" },
  {
    id: "5d000000-0000-4000-8000-000000000010",
    code: "TC-10",
    title: "Old checkout",
    storyKey: "SHOP-3",
    status: "deprecated",
  },
];

const suite = buildSuiteDetail({ cases: buildSuiteDetail().cases.slice(0, 2), caseCount: 2 });

describe("AddCasesModal", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    respondWithRoutes(apiGet, {
      [TEST_CASES_PATH]: createSuccessResult(PROJECT_CASES),
      [STORIES_PATH]: createSuccessResult([]),
    });
  });

  it("lists the cases that can be added and marks those already in the suite", async () => {
    const { container } = renderWithProject(
      <AddCasesModal projectKey="SHOP" suite={suite} onClose={vi.fn()} />,
      QC_PROJECT,
    );

    const inSuite = await screen.findByRole("checkbox", { name: "TC-1 · Pay with a valid card" });
    expect(inSuite).toBeChecked();
    expect(inSuite).toBeDisabled();
    expect(screen.getByText(`SHOP-1 · ${addCases.alreadyAdded}`)).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "TC-9 · Pay in two parts" })).not.toBeChecked();
    expect(screen.queryByRole("checkbox", { name: "TC-10 · Old checkout" })).toBeNull();
    expect(
      within(screen.getByRole("dialog")).getByRole("button", { name: addCases.add }),
    ).toBeDisabled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("searches the project's cases by code or title", async () => {
    const user = userEvent.setup();
    renderWithProject(
      <AddCasesModal projectKey="SHOP" suite={suite} onClose={vi.fn()} />,
      QC_PROJECT,
    );
    await screen.findByRole("checkbox", { name: "TC-9 · Pay in two parts" });

    await user.type(screen.getByRole("textbox", { name: addCases.search }), "two parts");

    await waitFor(() => {
      const queries = apiGet.mock.calls
        .filter(([path]) => path === TEST_CASES_PATH)
        .map(([, options]) => (options as ListRequest).params.query);
      expect(queries).toContainEqual({ query: "two parts" });
    });
  });

  it("appends the chosen cases to the suite", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    respondWithRoutes(apiPut, { [CASES_PATH]: createSuccessResult(buildSuiteDetail()) });
    renderWithProject(
      <AddCasesModal projectKey="SHOP" suite={suite} onClose={onClose} />,
      QC_PROJECT,
    );

    await user.click(await screen.findByRole("checkbox", { name: "TC-9 · Pay in two parts" }));
    expect(screen.getByText("1 case selected")).toBeInTheDocument();
    await user.click(
      within(screen.getByRole("dialog")).getByRole("button", { name: addCases.add }),
    );

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(CASES_PATH, {
        params: { path: { project_key: "SHOP", suite_id: SUITE_ID } },
        body: { testCaseIds: [CASE_IDS[0], CASE_IDS[1], NEW_CASE_ID] },
      });
    });
    expect(await screen.findByText("1 case added")).toBeInTheDocument();
    expect(onClose).toHaveBeenCalled();
  });
});
