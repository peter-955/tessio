import englishLabels from "@/lib/i18n/locales/en/labels.json";
import { GET_TEST_CASE_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-case";
import { buildTestCaseDetail } from "@/modules/test-cases/test/utils/test-case-fixture.util";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost, apiPut } from "../../test/mocks/api-client.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { buildLabel, CHECKOUT_LABEL_ID, toCaseLabel } from "../../test/utils/label-fixture.util";
import { buildProject, QC_CAPABILITIES } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { openSelectOption } from "../../test/utils/select-option.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { CaseLabelPicker } from "./case-label-picker";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const LABELS_PATH = "/api/projects/{project_key}/labels";
const CASE_LABELS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/labels";
const NEW_LABEL_ID = "c1000000-0000-4000-8000-000000000003";

const smoke = buildLabel();
const checkout = buildLabel({ id: CHECKOUT_LABEL_ID, name: "checkout", color: "blue" });
const qcProject = buildProject({ myRole: "qc", capabilities: QC_CAPABILITIES });

interface PutOptions {
  params: { path: { project_key: string; case_code: string } };
  body: { labelIds: string[] };
}

const renderPicker = (
  labels = [toCaseLabel(smoke)],
  canEdit = true,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <CaseLabelPicker projectKey="SHOP" caseCode="TC-1" labels={labels} canEdit={canEdit} />,
    qcProject,
  );
};

const startEditing = async (user: UserEvent): Promise<void> => {
  await user.click(await screen.findByRole("button", { name: englishLabels.picker.edit }));
};

const findLabelsField = (): HTMLElement => {
  return screen.getByRole("combobox", { name: new RegExp(`^${englishLabels.picker.field}`) });
};

describe("CaseLabelPicker", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    respondWithRoutes(apiGet, { [LABELS_PATH]: createSuccessResult([checkout, smoke]) });
    apiPut.mockImplementation((_path, options) => {
      const { body } = options as PutOptions;
      const labels = [checkout, smoke, buildLabel({ id: NEW_LABEL_ID, name: "regression" })]
        .filter((label) => body.labelIds.includes(label.id))
        .map(toCaseLabel);

      return Promise.resolve(createSuccessResult(labels));
    });
  });

  it("shows the case's labels as chips without an edit button for a reader", async () => {
    const { container } = renderPicker([toCaseLabel(smoke)], false);

    const chips = screen.getByRole("list", { name: englishLabels.chips.ariaLabel });
    expect(within(chips).getByText("smoke")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: englishLabels.picker.edit })).toBeNull();
    expect(apiGet).not.toHaveBeenCalled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("says when the case has no labels", () => {
    renderPicker([], false);

    expect(screen.getByText(englishLabels.picker.none)).toBeInTheDocument();
  });

  it("adds a project label and saves the case's labels in one request", async () => {
    const user = userEvent.setup();
    const { container, queryClient } = renderPicker();
    queryClient.setQueryData<TestCaseDetail>(
      [GET_TEST_CASE_KEY, "SHOP", "TC-1"],
      buildTestCaseDetail({ labels: [toCaseLabel(smoke)] }),
    );

    await startEditing(user);
    await waitFor(() => {
      expect(findLabelsField()).toBeEnabled();
    });
    await user.click(
      await openSelectOption(user, new RegExp(englishLabels.picker.field), "checkout"),
    );
    await user.click(screen.getByRole("button", { name: englishLabels.picker.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(CASE_LABELS_PATH, {
        params: { path: { project_key: "SHOP", case_code: "TC-1" } },
        body: { labelIds: [smoke.id, checkout.id] },
      });
    });
    expect(await screen.findByText(englishLabels.toasts.caseLabelsSaved)).toBeInTheDocument();
    expect(
      queryClient.getQueryData<TestCaseDetail>([GET_TEST_CASE_KEY, "SHOP", "TC-1"])?.labels,
    ).toEqual([toCaseLabel(checkout), toCaseLabel(smoke)]);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("creates a label by name and adds it to the case", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [LABELS_PATH]: createCreatedResult(
        buildLabel({ id: NEW_LABEL_ID, name: "regression", color: "gray", caseCount: 0 }),
      ),
    });
    renderPicker();

    await startEditing(user);
    await user.type(
      screen.getByRole("textbox", { name: englishLabels.picker.newLabel }),
      "  regression ",
    );
    await user.click(screen.getByRole("button", { name: englishLabels.picker.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(LABELS_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: { name: "regression", color: "gray" },
      });
    });
    await waitFor(() => {
      expect(screen.getByRole("textbox", { name: englishLabels.picker.newLabel })).toHaveValue("");
    });
    await user.click(screen.getByRole("button", { name: englishLabels.picker.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(CASE_LABELS_PATH, {
        params: { path: { project_key: "SHOP", case_code: "TC-1" } },
        body: { labelIds: [smoke.id, NEW_LABEL_ID] },
      });
    });
  });

  it("picks the existing label when the new name is already used", async () => {
    const user = userEvent.setup();
    renderPicker();

    await startEditing(user);
    await waitFor(() => {
      expect(findLabelsField()).toBeEnabled();
    });
    await user.type(
      screen.getByRole("textbox", { name: englishLabels.picker.newLabel }),
      "CHECKOUT",
    );
    await user.click(screen.getByRole("button", { name: englishLabels.picker.create }));
    await user.click(screen.getByRole("button", { name: englishLabels.picker.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(CASE_LABELS_PATH, {
        params: { path: { project_key: "SHOP", case_code: "TC-1" } },
        body: { labelIds: [smoke.id, checkout.id] },
      });
    });
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows a name error and sends nothing for a name that is too long", async () => {
    const user = userEvent.setup();
    renderPicker();

    await startEditing(user);
    await user.type(
      screen.getByRole("textbox", { name: englishLabels.picker.newLabel }),
      "a".repeat(41),
    );
    await user.click(screen.getByRole("button", { name: englishLabels.picker.create }));

    expect(
      await screen.findByText(englishLabels.validation.tooLong.replace("{{max}}", "40")),
    ).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows the name conflict the server reports on the new-label field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [LABELS_PATH]: createErrorResult(409, "CONFLICT") });
    renderPicker();

    await startEditing(user);
    await waitFor(() => {
      expect(findLabelsField()).toBeEnabled();
    });
    await user.type(screen.getByRole("textbox", { name: englishLabels.picker.newLabel }), "Fresh");
    await user.click(screen.getByRole("button", { name: englishLabels.picker.create }));

    expect(await screen.findByText(englishLabels.errors.nameAlreadyUsed)).toBeInTheDocument();
  });

  it("closes without a request when nothing changed", async () => {
    const user = userEvent.setup();
    renderPicker();

    await startEditing(user);
    await user.click(screen.getByRole("button", { name: englishLabels.picker.save }));

    expect(await screen.findByRole("button", { name: englishLabels.picker.edit })).toBeVisible();
    expect(apiPut).not.toHaveBeenCalled();
  });
});
