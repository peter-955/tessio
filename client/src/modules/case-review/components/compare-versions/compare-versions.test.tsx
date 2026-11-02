import englishCaseReview from "@/lib/i18n/locales/en/caseReview.json";
import { apiGet } from "@/modules/test-cases/test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/test-cases/test/utils/api-result.util";
import { interpolate } from "@/modules/test-cases/test/utils/interpolate.util";
import { buildProject } from "@/modules/test-cases/test/utils/project-fixture.util";
import { renderWithProject } from "@/modules/test-cases/test/utils/render-with-project.util";
import { openSelectOption } from "@/modules/test-cases/test/utils/select-option.util";
import { stubScrollIntoView } from "@/modules/test-cases/test/utils/stub-scroll-into-view.util";
import {
  buildMember,
  buildTestCaseDetail,
  buildTestCaseVersion,
  FORMER_USER_ID,
} from "@/modules/test-cases/test/utils/test-case-fixture.util";
import type { TestCaseVersion } from "@/modules/test-cases/typing/types/test-case.type";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { CompareVersions } from "./compare-versions";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("@/modules/test-cases/test/mocks/api-client.mock")).apiClientMock;
});

const VERSIONS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/versions";
const MEMBERS_PATH = "/api/projects/{project_key}/members";

const { compare } = englishCaseReview;

const FIRST_VERSION = buildTestCaseVersion({
  id: "a2000000-0000-4000-8000-000000000001",
  number: 1,
  title: "Pay by card",
  steps: [{ order: 1, action: "Open the cart", expected: null, sharedStepKey: null }],
  createdBy: FORMER_USER_ID,
});

const SECOND_VERSION = buildTestCaseVersion({
  id: "a2000000-0000-4000-8000-000000000002",
  number: 2,
  title: "Pay with a valid card",
  steps: [
    { order: 1, action: "Open the cart", expected: null, sharedStepKey: null },
    { order: 2, action: "Pay with a card", expected: "The order is paid", sharedStepKey: null },
  ],
});

const THIRD_VERSION = buildTestCaseVersion({
  id: "a2000000-0000-4000-8000-000000000003",
  number: 3,
  title: "Pay with a valid card",
  steps: [
    { order: 1, action: "Open the cart", expected: null, sharedStepKey: null },
    {
      order: 2,
      action: "Pay with a saved card",
      expected: "The order is paid",
      sharedStepKey: null,
    },
  ],
});

const respondWithVersions = (versions: TestCaseVersion[]): void => {
  respondWithRoutes(apiGet, {
    [VERSIONS_PATH]: createSuccessResult(versions),
    [MEMBERS_PATH]: createSuccessResult([buildMember()]),
  });
};

const renderCompare = (
  current: TestCaseVersion = THIRD_VERSION,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <CompareVersions detail={buildTestCaseDetail({ currentVersion: current })} />,
    buildProject(),
  );
};

const findRow = (table: HTMLElement, name: string): HTMLElement => {
  const header = within(table).getByRole("rowheader", { name: new RegExp(`^${name}`) });
  const row = header.closest("tr");
  if (row === null) {
    throw new Error(`No row for ${name}`);
  }

  return row;
};

describe("CompareVersions", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
  });

  it("puts the previous and the current version side by side and marks what changed", async () => {
    respondWithVersions([THIRD_VERSION, SECOND_VERSION, FIRST_VERSION]);
    const { container } = renderCompare();

    const table = await screen.findByRole("region", {
      name: interpolate(compare.tableLabel, { from: "2", to: "3" }),
    });
    const headers = within(table).getAllByRole("columnheader");
    expect(headers[1]).toHaveTextContent(/^Version 2 · Quinn Tester, /);
    expect(headers[2]).toHaveTextContent(/^Version 3 · Quinn Tester, /);
    expect(
      screen.getByText(interpolate(compare.changeCount_one, { count: "1" })),
    ).toBeInTheDocument();

    const changedStep = findRow(table, interpolate(compare.step, { order: "2" }));
    expect(within(changedStep).getByText(compare.kind.changed)).toBeInTheDocument();
    const inserted = changedStep.querySelector("ins");
    expect(inserted).toHaveTextContent(`${compare.added}: saved`);
    expect(changedStep.querySelector("del")).toBeNull();

    const sameStep = findRow(table, interpolate(compare.step, { order: "1" }));
    expect(within(sameStep).queryByText(compare.kind.changed)).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("compares any two picked versions and can hide the unchanged rows", async () => {
    const user = userEvent.setup();
    respondWithVersions([THIRD_VERSION, SECOND_VERSION, FIRST_VERSION]);
    renderCompare();
    await screen.findByRole("region", {
      name: interpolate(compare.tableLabel, { from: "2", to: "3" }),
    });

    await user.click(
      await openSelectOption(
        user,
        new RegExp(`^${compare.from}`),
        interpolate(compare.versionOption, { number: "1" }),
      ),
    );

    const table = await screen.findByRole("region", {
      name: interpolate(compare.tableLabel, { from: "1", to: "3" }),
    });
    expect(within(table).getAllByRole("columnheader")[1]).toHaveTextContent(
      /^Version 1 · Former member, /,
    );
    const titleRow = findRow(table, compare.fields.title);
    expect(titleRow.querySelector("del")).toHaveTextContent(`${compare.removed}: by`);
    const addedStep = findRow(table, interpolate(compare.step, { order: "2" }));
    expect(within(addedStep).getByText(compare.kind.added)).toBeInTheDocument();
    expect(within(addedStep).getByText(compare.noStep)).toBeInTheDocument();
    expect(findRow(table, interpolate(compare.step, { order: "1" }))).toBeInTheDocument();

    await user.click(screen.getByRole("switch", { name: compare.onlyChanges }));

    expect(
      within(table).queryByRole("rowheader", {
        name: interpolate(compare.step, { order: "1" }),
      }),
    ).toBeNull();
    expect(within(table).queryByRole("rowheader", { name: compare.fields.priority })).toBeNull();
    expect(findRow(table, compare.fields.title)).toBeInTheDocument();
  });

  it("says when the picked versions are the same", async () => {
    const user = userEvent.setup();
    respondWithVersions([THIRD_VERSION, SECOND_VERSION]);
    renderCompare();
    await screen.findByRole("region", {
      name: interpolate(compare.tableLabel, { from: "2", to: "3" }),
    });

    await user.click(
      await openSelectOption(
        user,
        new RegExp(`^${compare.from}`),
        interpolate(compare.currentOption, { number: "3" }),
      ),
    );

    expect(await screen.findByText(compare.identical)).toBeInTheDocument();
  });

  it("shows a version that changes only the data rows as a change, not as identical", async () => {
    const withRows = buildTestCaseVersion({
      ...SECOND_VERSION,
      parameters: ["email"],
      dataRows: [{ email: "ann" }],
    });
    const withOtherRows = buildTestCaseVersion({
      ...THIRD_VERSION,
      steps: SECOND_VERSION.steps,
      parameters: ["email"],
      dataRows: [{ email: "bob" }],
    });
    respondWithVersions([withOtherRows, withRows]);
    renderCompare(withOtherRows);

    const table = await screen.findByRole("region", {
      name: interpolate(compare.tableLabel, { from: "2", to: "3" }),
    });

    expect(
      screen.getByText(interpolate(compare.changeCount_one, { count: "1" })),
    ).toBeInTheDocument();
    expect(screen.queryByText(compare.identical)).toBeNull();
    const dataRow = findRow(table, compare.fields.dataTable);
    expect(within(dataRow).getByText(compare.kind.changed)).toBeInTheDocument();
    expect(dataRow.querySelector("del")).toHaveTextContent(`${compare.removed}: ann`);
    expect(dataRow.querySelector("ins")).toHaveTextContent(`${compare.added}: bob`);
  });

  it("explains that a case with one version has nothing to compare", async () => {
    respondWithVersions([FIRST_VERSION]);
    renderCompare(FIRST_VERSION);

    expect(await screen.findByText(compare.single)).toBeInTheDocument();
    expect(screen.queryByRole("combobox")).toBeNull();
  });

  it("offers a retry when the versions cannot be loaded", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [VERSIONS_PATH]: createErrorResult(429, "RATE_LIMITED"),
      [MEMBERS_PATH]: createSuccessResult([]),
    });
    renderCompare();

    expect(await screen.findByText(compare.loadError)).toBeInTheDocument();
    respondWithVersions([THIRD_VERSION, SECOND_VERSION]);
    await user.click(screen.getByRole("button", { name: englishCaseReview.retry }));

    expect(
      await screen.findByRole("region", {
        name: interpolate(compare.tableLabel, { from: "2", to: "3" }),
      }),
    ).toBeInTheDocument();
  });
});
