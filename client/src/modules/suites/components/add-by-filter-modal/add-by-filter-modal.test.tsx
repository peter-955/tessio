import englishSuites from "@/lib/i18n/locales/en/suites.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { buildLabel, CHECKOUT_LABEL_ID } from "@/modules/labels/test/utils/label-fixture.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { openSelectOption } from "../../test/utils/select-option.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { QC_PROJECT } from "../../test/utils/suite-project.util";
import { buildSuiteDetail, SUITE_ID } from "../../test/utils/suite.fixture";
import { AddByFilterModal } from "./add-by-filter-modal";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const LABELS_PATH = "/api/projects/{project_key}/labels";
const SPRINTS_PATH = "/api/projects/{project_key}/sprints";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const BY_FILTER_PATH = "/api/projects/{project_key}/suites/{suite_id}/cases/by-filter";
const SPRINT_ID = "5f000000-0000-4000-8000-000000000001";

const { filter } = englishSuites;

const renderModal = (onClose = vi.fn()): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <AddByFilterModal projectKey="SHOP" suiteId={SUITE_ID} onClose={onClose} />,
    QC_PROJECT,
  );
};

const findAddButton = async (): Promise<HTMLElement> => {
  return within(await screen.findByRole("dialog")).findByRole("button", { name: filter.add });
};

describe("AddByFilterModal", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    respondWithRoutes(apiGet, {
      [LABELS_PATH]: createSuccessResult([
        buildLabel(),
        buildLabel({ id: CHECKOUT_LABEL_ID, name: "checkout", color: "blue" }),
      ]),
      [SPRINTS_PATH]: createSuccessResult([{ id: SPRINT_ID, name: "Sprint 12" }]),
      [STORIES_PATH]: createSuccessResult([{ jiraKey: "SHOP-1", title: "Pay by card" }]),
    });
  });

  it("asks for a filter before it can add cases", async () => {
    const { container } = renderModal();

    expect(await findAddButton()).toBeDisabled();
    expect(screen.getByText(filter.required)).toBeInTheDocument();
    expect(screen.getByText(filter.description)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("sends the chosen labels, priority, story and sprint and says how many were added", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    respondWithRoutes(apiPost, {
      [BY_FILTER_PATH]: createSuccessResult({ addedCount: 2, suite: buildSuiteDetail() }),
    });
    renderModal(onClose);

    await user.click(await openSelectOption(user, /^Labels/, "smoke"));
    await user.click(await openSelectOption(user, /^Labels/, "checkout"));
    await user.click(await openSelectOption(user, /^Priorities/, "High"));
    await user.click(await openSelectOption(user, /^Story/, "SHOP-1 · Pay by card"));
    await user.click(await openSelectOption(user, /^Sprint/, "Sprint 12"));
    await user.click(await findAddButton());

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(BY_FILTER_PATH, {
        params: { path: { project_key: "SHOP", suite_id: SUITE_ID } },
        body: {
          labels: ["smoke", "checkout"],
          priorities: ["high"],
          storyKey: "SHOP-1",
          sprintId: SPRINT_ID,
        },
      });
    });
    expect(await screen.findByText("2 cases added")).toBeInTheDocument();
    expect(onClose).toHaveBeenCalled();
  });

  it("says so when no new case matched", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [BY_FILTER_PATH]: createSuccessResult({ addedCount: 0, suite: buildSuiteDetail() }),
    });
    renderModal();

    await user.click(await openSelectOption(user, /^Priorities/, "Low"));
    await user.click(await findAddButton());

    expect(await screen.findByText(filter.noneAdded)).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith(BY_FILTER_PATH, {
      params: { path: { project_key: "SHOP", suite_id: SUITE_ID } },
      body: { priorities: ["low"] },
    });
  });

  it("keeps the dialog open with the reason when the server refuses", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    respondWithRoutes(apiPost, {
      [BY_FILTER_PATH]: createErrorResult(422, "UNKNOWN_REFERENCE"),
    });
    renderModal(onClose);

    await user.click(await openSelectOption(user, /^Story/, "SHOP-1 · Pay by card"));
    await user.click(await findAddButton());

    expect(await screen.findByText(englishSuites.errors.unknownReference)).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
  });
});
