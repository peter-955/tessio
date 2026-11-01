import { ApiError } from "@/lib/api/api-error";
import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiPost } from "../../test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { interpolate } from "../../test/utils/interpolate.util";
import { buildProject, QC_CAPABILITIES } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import {
  buildUploadedFile,
  resetUpload,
  UPLOADED_FILE_ID,
  uploadFile,
} from "../../test/utils/signed-upload-stub.util";
import { stubDocumentFonts } from "../../test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { buildImportItem } from "../../test/utils/test-case-fixture.util";
import { CSV_CONTENT_TYPE, XLSX_CONTENT_TYPE } from "../../typing/constants/test-case.constant";
import { ImportWizard } from "./import-wizard";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("@/lib/uploads/hooks/use-signed-upload", async () => {
  return (await import("../../test/utils/signed-upload-stub.util")).signedUploadMock;
});

const PREVIEW_PATH = "/api/projects/{project_key}/test-case-imports/preview";
const COMMIT_PATH = "/api/projects/{project_key}/test-case-imports/commit";

const { import: importText, toasts } = englishTestCases;

const PREVIEW = {
  format: "csv",
  items: [
    buildImportItem({ index: 0, title: "Pay with a valid card" }),
    buildImportItem({
      index: 1,
      title: "Pay twice",
      isDuplicate: true,
      criterionCodes: ["AC1", "AC9"],
      unknownCriterionCodes: ["AC9"],
    }),
    buildImportItem({
      index: 2,
      title: "Ghost story",
      storyKey: "SHOP-99",
      problem: "story_not_found",
    }),
  ],
  skipped: [{ location: "SHOP-1!A9", reason: "step_without_case" }],
};

const handleClose = vi.fn<() => void>();

const renderWizard = (): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <ImportWizard onClose={handleClose} />,
    buildProject({ capabilities: QC_CAPABILITIES }),
  );
};

const chooseFile = async (user: UserEvent, file: File): Promise<HTMLElement> => {
  const dialog = await screen.findByRole("dialog", { name: importText.title });
  const input = dialog.querySelector<HTMLInputElement>('input[type="file"]') as HTMLInputElement;
  await user.upload(input, file);

  return dialog;
};

const findIncludeBox = (dialog: HTMLElement, title: string): HTMLElement => {
  return within(dialog).getByRole("checkbox", {
    name: interpolate(importText.includeItem, { title }),
  });
};

describe("ImportWizard", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiPost.mockReset();
    uploadFile.mockReset();
    resetUpload.mockReset();
    handleClose.mockReset();
    uploadFile.mockImplementation((file) => Promise.resolve(buildUploadedFile(file, "import")));
    respondWithRoutes(apiPost, {
      [PREVIEW_PATH]: createSuccessResult(PREVIEW),
      [COMMIT_PATH]: createSuccessResult({
        created: [
          { code: "TC-8", storyKey: "SHOP-1", title: "Pay with a valid card" },
          { code: "TC-9", storyKey: "SHOP-1", title: "Pay twice" },
        ],
      }),
    });
  });

  it("previews the cases with duplicates unchecked and problems locked, then commits", async () => {
    const user = userEvent.setup();
    renderWizard();

    const dialog = await chooseFile(user, new File(["Story,Title"], "cases.csv"));

    expect(uploadFile.mock.calls[0]?.[0].type).toBe(CSV_CONTENT_TYPE);
    expect(apiPost).toHaveBeenCalledWith(PREVIEW_PATH, {
      params: { path: { project_key: "SHOP" } },
      body: { fileId: UPLOADED_FILE_ID },
    });
    expect(
      await within(dialog).findByText(interpolate(importText.format, { format: "CSV" })),
    ).toBeInTheDocument();
    expect(findIncludeBox(dialog, "Pay with a valid card")).toBeChecked();
    expect(findIncludeBox(dialog, "Pay twice")).not.toBeChecked();
    expect(findIncludeBox(dialog, "Ghost story")).toBeDisabled();
    expect(within(dialog).getByText(importText.duplicate)).toBeInTheDocument();
    expect(within(dialog).getByText(importText.problems.story_not_found)).toBeInTheDocument();
    expect(
      within(dialog).getByText(interpolate(importText.unknownCriteria, { codes: "AC9" })),
    ).toBeInTheDocument();
    expect(within(dialog).getByText(importText.skipReasons.step_without_case)).toBeInTheDocument();

    await user.click(findIncludeBox(dialog, "Pay twice"));
    await user.click(
      within(dialog).getByRole("button", { name: interpolate(importText.commit, { count: "2" }) }),
    );

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(COMMIT_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: { fileId: UPLOADED_FILE_ID, indexes: [0, 1] },
      });
    });
    expect(
      await screen.findByText(interpolate(toasts.imported_other, { count: "2" })),
    ).toBeInTheDocument();
    expect(handleClose).toHaveBeenCalled();
  });

  it("disables the commit when nothing is selected", async () => {
    const user = userEvent.setup();
    renderWizard();

    const dialog = await chooseFile(user, new File(["x"], "cases.xlsx"));

    expect(uploadFile.mock.calls[0]?.[0].type).toBe(XLSX_CONTENT_TYPE);
    await user.click(await within(dialog).findByRole("checkbox", { name: importText.selectAll }));
    await user.click(within(dialog).getByRole("checkbox", { name: importText.selectAll }));

    expect(
      within(dialog).getByRole("button", { name: interpolate(importText.commit, { count: "0" }) }),
    ).toBeDisabled();
    expect(within(dialog).getByText(importText.nothingSelected)).toBeInTheDocument();
  });

  it("rejects other file types before uploading", async () => {
    const user = userEvent.setup();
    renderWizard();

    const dialog = await chooseFile(user, new File(["x"], "cases.txt"));

    expect(await within(dialog).findByText(importText.errors.extension)).toBeInTheDocument();
    expect(uploadFile).not.toHaveBeenCalled();
  });

  it("asks for the file types when the project does not allow them", async () => {
    const user = userEvent.setup();
    uploadFile.mockRejectedValue(
      new ApiError({ status: 422, code: "FILE_TYPE_NOT_ALLOWED", message: "Not allowed" }),
    );
    renderWizard();

    const dialog = await chooseFile(user, new File(["x"], "cases.csv"));

    expect(await within(dialog).findByText(importText.errors.typeNotAllowed)).toBeInTheDocument();
  });

  it("explains a file that cannot be read", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [PREVIEW_PATH]: createErrorResult(422, "IMPORT_INVALID_FILE") });
    renderWizard();

    const dialog = await chooseFile(user, new File(["x"], "cases.csv"));

    expect(await within(dialog).findByText(importText.errors.invalidFile)).toBeInTheDocument();
  });

  it("has no axe violations, reaches the dropzone by Tab and closes on Escape", async () => {
    const user = userEvent.setup();
    renderWizard();

    const dialog = await screen.findByRole("dialog", { name: importText.title });
    expect(await axe(dialog)).toHaveNoViolations();
    await tabTo(user, within(dialog).getByRole("button", { name: importText.dropTitle }));

    await chooseFile(user, new File(["Story,Title"], "cases.csv"));
    expect(
      await within(dialog).findByRole("region", { name: importText.previewCaption }),
    ).toBeInTheDocument();
    expect(await axe(dialog)).toHaveNoViolations();

    await user.keyboard("{Escape}");
    expect(handleClose).toHaveBeenCalled();
  });
});
