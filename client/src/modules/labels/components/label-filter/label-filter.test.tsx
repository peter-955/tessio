import englishLabels from "@/lib/i18n/locales/en/labels.json";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet } from "../../test/mocks/api-client.mock";
import { createSuccessResult, respondWithRoutes } from "../../test/utils/api-result.util";
import { buildLabel, CHECKOUT_LABEL_ID } from "../../test/utils/label-fixture.util";
import { buildProject } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { openSelectOption } from "../../test/utils/select-option.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { LabelFilter } from "./label-filter";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const LABELS_PATH = "/api/projects/{project_key}/labels";
const FILTER_LABEL = new RegExp(`^${englishLabels.filter.label}`);

const smoke = buildLabel();
const checkout = buildLabel({ id: CHECKOUT_LABEL_ID, name: "Checkout", color: "blue" });

describe("LabelFilter", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    respondWithRoutes(apiGet, { [LABELS_PATH]: createSuccessResult([checkout, smoke]) });
  });

  it("filters by the names of the chosen labels", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn<(labelNames: string[]) => void>();
    const { container } = renderWithProject(
      <LabelFilter value={["smoke"]} onChange={handleChange} />,
      buildProject(),
    );

    await screen.findByRole("combobox", { name: FILTER_LABEL });
    await user.click(await openSelectOption(user, FILTER_LABEL, "Checkout"));

    expect(handleChange).toHaveBeenCalledWith(["smoke", "Checkout"]);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows a name from the URL in the label's own case", async () => {
    const handleChange = vi.fn<(labelNames: string[]) => void>();
    const { container } = renderWithProject(
      <LabelFilter value={["checkout"]} onChange={handleChange} />,
      buildProject(),
    );

    await waitFor(() => {
      const pills = [...container.querySelectorAll(".mantine-Pill-label")];
      expect(pills.map((pill) => pill.textContent)).toEqual(["Checkout"]);
    });
    expect(handleChange).not.toHaveBeenCalled();
  });

  it("is hidden while the project has no labels and none is chosen", async () => {
    respondWithRoutes(apiGet, { [LABELS_PATH]: createSuccessResult([]) });
    renderWithProject(<LabelFilter value={[]} onChange={vi.fn()} />, buildProject());

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith(LABELS_PATH, expect.anything());
    });
    expect(screen.queryByRole("combobox", { name: FILTER_LABEL })).toBeNull();
  });
});
