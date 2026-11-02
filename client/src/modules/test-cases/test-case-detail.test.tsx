import englishCaseReview from "@/lib/i18n/locales/en/caseReview.json";
import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import { buildReviewComment } from "@/modules/case-review/test/utils/review-comment-fixture.util";
import type { ReviewComment } from "@/modules/case-review/typing/types/review-comment.type";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GET_TEST_CASE_KEY, type GetTestCaseQueryKey } from "./hooks/queries/use-get-test-case";
import { TestCaseDetailPage } from "./test-case-detail";
import { apiGet, apiPatch, apiPost, apiPut } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { interpolate } from "./test/utils/interpolate.util";
import { buildProject, QC_CAPABILITIES } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  buildUploadedFile,
  resetUpload,
  UPLOADED_FILE_ID,
  uploadFile,
} from "./test/utils/signed-upload-stub.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import {
  buildMember,
  buildStoryDetail,
  buildTestCaseDetail,
  buildTestCaseVersion,
  buildTestFile,
  buildTestFileVersion,
  FIRST_CRITERION_ID,
  FORMER_USER_ID,
  SECOND_CRITERION_ID,
} from "./test/utils/test-case-fixture.util";
import { TestCaseDetailTab } from "./typing/enums/test-case-detail-tab.enum";
import type { TestCaseDetail } from "./typing/types/test-case.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("@/lib/uploads/hooks/use-signed-upload", async () => {
  return (await import("./test/utils/signed-upload-stub.util")).signedUploadMock;
});

const CASE_PATH = "/api/projects/{project_key}/test-cases/{case_code}";
const VERSIONS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/versions";
const STATUS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/status";
const REVIEW_PATH = "/api/projects/{project_key}/test-cases/{case_code}/review";
const FILES_PATH = "/api/projects/{project_key}/test-cases/{case_code}/files";
const FILE_VERSIONS_PATH =
  "/api/projects/{project_key}/test-cases/{case_code}/files/{file_key}/versions";
const DOWNLOAD_PATH = "/api/projects/{project_key}/files/{file_id}";
const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";
const EFFECTIVE_TEST_DATA_PATH = "/api/projects/{project_key}/test-data/effective";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const MEMBERS_PATH = "/api/projects/{project_key}/members";
const REVIEW_COMMENTS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/review-comments";
const QUARANTINE_EVENTS_PATH =
  "/api/projects/{project_key}/test-cases/{case_code}/quarantine-events";
const CASE_PARAMS = { params: { path: { project_key: "SHOP", case_code: "TC-1" } } };

const { actions, deprecateConfirm, detail, errors, files, form, history, read, status, toasts } =
  englishTestCases;

const DETAIL = buildTestCaseDetail();

const OLDER_VERSION = buildTestCaseVersion({
  id: "a2000000-0000-4000-8000-000000000001",
  number: 1,
  title: "Pay with a card",
  createdBy: FORMER_USER_ID,
});

const OPEN_REVIEW_COMMENT = buildReviewComment();

const respondWithCase = (
  testCase: TestCaseDetail | (() => ApiResult),
  reviewComments: ReviewComment[] = [],
): void => {
  respondWithRoutes(apiGet, {
    [CASE_PATH]: typeof testCase === "function" ? testCase : createSuccessResult(testCase),
    [VERSIONS_PATH]: createSuccessResult([DETAIL.currentVersion, OLDER_VERSION]),
    [FILE_VERSIONS_PATH]: createSuccessResult([
      buildTestFileVersion({ id: "a3000000-0000-4000-8000-000000000002", number: 2 }),
      buildTestFileVersion(),
    ]),
    [DOWNLOAD_PATH]: createSuccessResult({
      url: "https://files.example.test/avatar.png",
      expiresAt: "2026-10-21T10:00:00Z",
    }),
    [STORY_PATH]: createSuccessResult(buildStoryDetail()),
    [TEST_DATA_PATH]: createSuccessResult([]),
    [EFFECTIVE_TEST_DATA_PATH]: createSuccessResult([
      {
        id: "a9000000-0000-4000-8000-000000000001",
        environmentId: null,
        key: "username",
        kind: "variable",
        value: "anna@shop.test",
        hasValue: true,
        createdAt: "2026-10-20T10:00:00Z",
      },
    ]),
    [ENVIRONMENTS_PATH]: createSuccessResult([]),
    [MEMBERS_PATH]: createSuccessResult([buildMember()]),
    [REVIEW_COMMENTS_PATH]: createSuccessResult(reviewComments),
    [QUARANTINE_EVENTS_PATH]: createSuccessResult([]),
  });
};

const renderPage = (
  capabilities = QC_CAPABILITIES,
  options: { caseCode?: string; initialTab?: TestCaseDetailTab; isArchived?: boolean } = {},
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <TestCaseDetailPage
      caseCode={options.caseCode ?? "TC-1"}
      initialTab={options.initialTab ?? TestCaseDetailTab.DETAILS}
    />,
    buildProject({ capabilities, isArchived: options.isArchived ?? false }),
  );
};

const withFileKey = (label: string): RegExp => {
  return new RegExp(`^${label}\\s+avatar$`);
};

const findTitleField = async (): Promise<HTMLElement> => {
  return screen.findByRole("textbox", { name: new RegExp(`^${form.title}`) });
};

const openEditor = async (user: UserEvent): Promise<void> => {
  await user.click(await screen.findByRole("button", { name: read.edit }));
};

const editTitle = async (user: UserEvent, title: string): Promise<void> => {
  if (screen.queryByRole("textbox", { name: new RegExp(`^${form.title}`) }) === null) {
    await openEditor(user);
  }
  const titleField = await findTitleField();
  await user.clear(titleField);
  await user.type(titleField, title);
};

describe("TestCaseDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    apiPatch.mockReset();
    uploadFile.mockReset();
    resetUpload.mockReset();
    routerReplace.mockReset();
    setNavigation("/projects/SHOP/test-cases/TC-1");
    respondWithCase(DETAIL);
  });

  it("shows the case as a read view with data values, then in the form on Edit", async () => {
    const user = userEvent.setup();
    const { container } = renderPage();

    expect(
      await screen.findByRole("heading", { level: 1, name: "TC-1 · Pay with a valid card" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "SHOP-1 · Pay by card" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-1",
    );
    expect(screen.getByText(interpolate(detail.version, { number: "2" }))).toBeInTheDocument();
    const steps = await screen.findByRole("region", { name: "Steps" });
    expect(within(steps).getByText("Open the cart")).toBeInTheDocument();
    expect(await within(steps).findByText("anna@shop.test")).toBeInTheDocument();
    expect(screen.queryByRole("textbox", { name: new RegExp(`^${form.title}`) })).toBeNull();
    expect(await axe(container)).toHaveNoViolations();

    await openEditor(user);
    expect(await findTitleField()).toHaveValue("Pay with a valid card");
    expect(
      screen
        .getAllByRole("textbox", { name: new RegExp(`^${form.action}`) })
        .map((field) => (field as HTMLTextAreaElement).value),
    ).toEqual(["Open the cart", "Pay as {{data.username}}"]);
    expect(screen.getByRole("button", { name: actions.save })).toBeDisabled();
    expect(screen.getByRole("button", { name: actions.submitForReview })).toBeEnabled();

    await user.click(screen.getByRole("button", { name: read.cancel }));
    expect(await screen.findByRole("button", { name: read.edit })).toBeInTheDocument();
  });

  it("saves only the changed fields on top of the current version", async () => {
    const user = userEvent.setup();
    const savedDetail = buildTestCaseDetail({
      title: "Pay with a saved card",
      currentVersion: buildTestCaseVersion({
        id: "a2000000-0000-4000-8000-000000000003",
        number: 3,
        title: "Pay with a saved card",
      }),
    });
    respondWithRoutes(apiPatch, { [CASE_PATH]: createSuccessResult(savedDetail) });
    renderPage();

    await editTitle(user, "Pay with a saved card");
    expect(screen.getByRole("button", { name: actions.submitForReview })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: actions.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(CASE_PATH, {
        ...CASE_PARAMS,
        body: { baseVersionNumber: 2, title: "Pay with a saved card" },
      });
    });
    expect(await screen.findByText(interpolate(toasts.saved, { number: "3" }))).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: read.edit })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.save })).toBeNull();
    expect(screen.getByRole("button", { name: actions.submitForReview })).toBeEnabled();
  });

  it("shows a reload alert when someone saved first", async () => {
    const user = userEvent.setup();
    const newerDetail = buildTestCaseDetail({
      title: "Pay with any card",
      currentVersion: buildTestCaseVersion({
        id: "a2000000-0000-4000-8000-000000000004",
        number: 3,
        title: "Pay with any card",
      }),
    });
    let isReloaded = false;
    respondWithCase(() => createSuccessResult(isReloaded ? newerDetail : DETAIL));
    respondWithRoutes(apiPatch, { [CASE_PATH]: createErrorResult(409, "CONFLICT") });
    renderPage();

    await editTitle(user, "Pay with my card");
    await user.click(screen.getByRole("button", { name: actions.save }));

    expect(await screen.findByText(errors.versionConflict)).toBeInTheDocument();
    isReloaded = true;
    await user.click(screen.getByRole("button", { name: actions.reload }));

    await waitFor(() => {
      expect(screen.queryByText(errors.versionConflict)).toBeNull();
    });
    expect(await findTitleField()).toHaveValue("Pay with any card");
  });

  it("follows a newer version while clean and keeps edits while dirty", async () => {
    const user = userEvent.setup();
    const { queryClient } = renderPage();
    const queryKey: GetTestCaseQueryKey = [GET_TEST_CASE_KEY, "SHOP", "TC-1"];

    await openEditor(user);
    await findTitleField();
    act(() => {
      queryClient.setQueryData(
        queryKey,
        buildTestCaseDetail({
          currentVersion: buildTestCaseVersion({
            id: "a2000000-0000-4000-8000-000000000006",
            number: 3,
            title: "Pay with a gift card",
          }),
        }),
      );
    });
    expect(await findTitleField()).toHaveValue("Pay with a gift card");

    await editTitle(user, "My own title");
    act(() => {
      queryClient.setQueryData(
        queryKey,
        buildTestCaseDetail({
          currentVersion: buildTestCaseVersion({
            id: "a2000000-0000-4000-8000-000000000007",
            number: 4,
            title: "Someone else's title",
          }),
        }),
      );
    });
    expect(await findTitleField()).toHaveValue("My own title");
  });

  it("submits a draft for review", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, {
      [STATUS_PATH]: createSuccessResult(buildTestCaseDetail({ status: "in_review" })),
    });
    renderPage();

    await user.click(await screen.findByRole("button", { name: actions.submitForReview }));

    expect(apiPut).toHaveBeenCalledWith(STATUS_PATH, {
      ...CASE_PARAMS,
      body: { status: "in_review" },
    });
    expect(
      await screen.findByText(
        interpolate(toasts.statusChanged, { code: "TC-1", status: status.in_review }),
      ),
    ).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: actions.markReady })).toBeInTheDocument();
  });

  it("explains why a case cannot be marked ready", async () => {
    const user = userEvent.setup();
    respondWithCase(buildTestCaseDetail({ status: "in_review" }));
    respondWithRoutes(apiPut, { [STATUS_PATH]: createErrorResult(409, "CASE_NOT_READY") });
    renderPage();

    await user.click(await screen.findByRole("button", { name: actions.markReady }));

    expect(await screen.findByText(errors.notReady)).toBeInTheDocument();
  });

  it("asks before deprecating", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, {
      [STATUS_PATH]: createSuccessResult(buildTestCaseDetail({ status: "deprecated" })),
    });
    renderPage();

    await user.click(await screen.findByRole("button", { name: actions.more }));
    await user.click(await screen.findByRole("menuitem", { name: actions.deprecate }));

    const dialog = await screen.findByRole("dialog", {
      name: interpolate(deprecateConfirm.title, { code: "TC-1" }),
    });
    expect(apiPut).not.toHaveBeenCalled();
    await user.click(within(dialog).getByRole("button", { name: actions.deprecate }));

    expect(apiPut).toHaveBeenCalledWith(STATUS_PATH, {
      ...CASE_PARAMS,
      body: { status: "deprecated" },
    });
    expect(await screen.findByRole("button", { name: actions.restore })).toBeInTheDocument();
  });

  it("clears the needs-review alert after Mark reviewed", async () => {
    const user = userEvent.setup();
    respondWithCase(
      buildTestCaseDetail({
        needsReview: true,
        needsReviewCriterionIds: [FIRST_CRITERION_ID, SECOND_CRITERION_ID],
        criteria: [
          { id: FIRST_CRITERION_ID, code: "AC1", text: "Card payment succeeds", isRemoved: false },
          { id: SECOND_CRITERION_ID, code: "AC2", text: "Declined", isRemoved: false },
        ],
      }),
    );
    respondWithRoutes(apiPost, { [REVIEW_PATH]: createSuccessResult(DETAIL) });
    renderPage();

    const alertText = interpolate(detail.needsReview, { codes: "AC1, AC2" });
    expect(await screen.findByText(alertText)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: actions.markReviewed }));

    expect(apiPost).toHaveBeenCalledWith(REVIEW_PATH, CASE_PARAMS);
    await waitFor(() => {
      expect(screen.queryByText(alertText)).toBeNull();
    });
  });

  it("lists unknown references", async () => {
    respondWithCase(buildTestCaseDetail({ unknownReferences: ["data.password", "file.avatar"] }));
    renderPage();

    expect(
      await screen.findByText(
        interpolate(detail.unknownReferences, {
          references: "{{data.password}}, {{file.avatar}}",
        }),
      ),
    ).toBeInTheDocument();
  });

  it("is read-only for a viewer", async () => {
    renderPage(buildProject().capabilities);

    expect(await screen.findByRole("region", { name: "Steps" })).toBeInTheDocument();
    expect(screen.getByText(form.readOnly)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: read.edit })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.save })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.submitForReview })).toBeNull();
    expect(screen.queryByRole("button", { name: form.addStep })).toBeNull();
  });

  it("is read-only on an archived project", async () => {
    renderPage(QC_CAPABILITIES, { isArchived: true });

    expect(await screen.findByRole("region", { name: "Steps" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: read.edit })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.save })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.submitForReview })).toBeNull();
  });

  it("only offers Restore on a deprecated case", async () => {
    respondWithCase(buildTestCaseDetail({ status: "deprecated" }));
    renderPage();

    expect(await screen.findByRole("region", { name: "Steps" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: read.edit })).toBeNull();
    expect(screen.getByText(form.deprecated)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: actions.restore })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.more })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.save })).toBeNull();
  });

  it("shows not found for a 404 and for an invalid code", async () => {
    respondWithCase(() => createErrorResult(404, "NOT_FOUND"));
    const { unmount } = renderPage();

    expect(await screen.findByText(detail.notFound.title)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: actions.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases",
    );
    unmount();
    apiGet.mockClear();

    renderPage(QC_CAPABILITIES, { caseCode: "CASE-1" });
    expect(screen.getByText(detail.notFound.title)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalledWith(CASE_PATH, expect.anything());
  });

  it("compares versions word by word", async () => {
    const user = userEvent.setup();
    const { container } = renderPage(QC_CAPABILITIES, { initialTab: TestCaseDetailTab.HISTORY });

    expect(
      await screen.findByText(interpolate(history.savedBy, { name: "Quinn Tester" })),
    ).toBeInTheDocument();
    expect(
      screen.getByText(interpolate(history.savedBy, { name: history.formerMember })),
    ).toBeInTheDocument();
    expect(screen.getByText(history.current)).toBeInTheDocument();
    const added = container.querySelector("ins");
    const removed = container.querySelector("del");
    expect(added?.textContent).toBe(`${history.diffAdded}: valid `);
    expect(removed).toBeNull();
    expect(screen.getByText(history.fields.title)).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: detail.tabs.details }));
    expect(routerReplace).toHaveBeenLastCalledWith("?tab=details", { scroll: false });
  });

  it("opens review comments from the open-comment alert and compares versions side by side", async () => {
    const user = userEvent.setup();
    respondWithCase(buildTestCaseDetail({ status: "in_review" }), [OPEN_REVIEW_COMMENT]);
    renderPage();

    const showComments = await screen.findByRole("button", {
      name: englishCaseReview.notice.showComments,
    });
    expect(screen.getByRole("button", { name: actions.markReady })).toBeDisabled();
    await user.click(showComments);

    expect(routerReplace).toHaveBeenLastCalledWith("?tab=review", { scroll: false });
    expect(await screen.findByText(OPEN_REVIEW_COMMENT.body)).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: englishCaseReview.tabs.compare }));

    expect(
      await screen.findByRole("region", {
        name: interpolate(englishCaseReview.compare.tableLabel, { from: "1", to: "2" }),
      }),
    ).toBeInTheDocument();
  });

  it("attaches a file through a signed upload", async () => {
    const user = userEvent.setup();
    const attachedDetail = buildTestCaseDetail({
      files: [buildTestFile({ key: "users" })],
      currentVersion: buildTestCaseVersion({
        id: "a2000000-0000-4000-8000-000000000005",
        number: 3,
      }),
    });
    uploadFile.mockImplementation((file) => Promise.resolve(buildUploadedFile(file, "test_file")));
    respondWithRoutes(apiPost, { [FILES_PATH]: createSuccessResult(attachedDetail) });
    renderPage(QC_CAPABILITIES, { initialTab: TestCaseDetailTab.FILES });

    expect(await screen.findByText(files.empty)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: actions.addFile }));
    const dialog = await screen.findByRole("dialog", { name: files.title });
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${files.key}`) }),
      "users",
    );
    expect(
      within(dialog).getByText(interpolate(files.keyHint, { reference: "{{file.users}}" })),
    ).toBeInTheDocument();
    const input = dialog.querySelector<HTMLInputElement>('input[type="file"]') as HTMLInputElement;
    await user.upload(input, new File(["name,email"], "users.csv", { type: "text/csv" }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(FILES_PATH, {
        ...CASE_PARAMS,
        body: { key: "users", fileId: UPLOADED_FILE_ID, baseVersionNumber: 2 },
      });
    });
    expect(uploadFile.mock.calls[0]?.[0].name).toBe("users.csv");
    expect(
      await screen.findByText(interpolate(toasts.fileAttached, { key: "users" })),
    ).toBeInTheDocument();
    expect(screen.queryByRole("dialog", { name: files.title })).toBeNull();
  });

  it("blocks file attachments until unsaved edits are saved", async () => {
    const user = userEvent.setup();
    respondWithCase(buildTestCaseDetail({ files: [buildTestFile()] }));
    renderPage();

    await editTitle(user, "Pay with any card");
    await user.click(screen.getByRole("tab", { name: new RegExp(`^${detail.tabs.files}`) }));

    const addFileButton = await screen.findByRole("button", { name: actions.addFile });
    expect(addFileButton).toBeDisabled();
    expect(addFileButton).toHaveAttribute("title", form.saveFirst);
    expect(screen.getByRole("button", { name: withFileKey(actions.newVersion) })).toBeDisabled();
  });

  it("uploads a new version, lists the versions and downloads them", async () => {
    const user = userEvent.setup();
    const openWindow = vi.spyOn(window, "open").mockReturnValue(null);
    respondWithCase(buildTestCaseDetail({ files: [buildTestFile()] }));
    respondWithRoutes(apiPost, { [FILES_PATH]: createErrorResult(409, "CONFLICT") });
    uploadFile.mockImplementation((file) => Promise.resolve(buildUploadedFile(file, "test_file")));
    renderPage(QC_CAPABILITIES, { initialTab: TestCaseDetailTab.FILES });

    await user.click(await screen.findByRole("button", { name: withFileKey(actions.download) }));
    await waitFor(() => {
      expect(openWindow).toHaveBeenCalledWith(
        "https://files.example.test/avatar.png",
        "_blank",
        "noopener",
      );
    });

    await user.click(screen.getByRole("button", { name: withFileKey(actions.versions) }));
    const drawer = await screen.findByRole("dialog", {
      name: interpolate(files.versionsTitle, { key: "avatar" }),
    });
    expect(await within(drawer).findAllByRole("listitem")).toHaveLength(2);
    await user.click(within(drawer).getByRole("button", { name: actions.close }));

    await user.click(screen.getByRole("button", { name: withFileKey(actions.newVersion) }));
    const dialog = await screen.findByRole("dialog", { name: actions.newVersion });
    expect(
      within(dialog).getByText(interpolate(files.newVersionHint, { number: "2", key: "avatar" })),
    ).toBeInTheDocument();
    const input = dialog.querySelector<HTMLInputElement>('input[type="file"]') as HTMLInputElement;
    await user.upload(input, new File(["x"], "avatar.txt", { type: "text/plain" }));

    expect(await within(dialog).findByText(errors.fileConflict)).toBeInTheDocument();
  });
});
