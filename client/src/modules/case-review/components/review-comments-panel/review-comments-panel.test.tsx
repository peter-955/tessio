import englishCaseReview from "@/lib/i18n/locales/en/caseReview.json";
import { apiGet, apiPost, apiPut } from "@/modules/test-cases/test/mocks/api-client.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/test-cases/test/utils/api-result.util";
import { interpolate } from "@/modules/test-cases/test/utils/interpolate.util";
import {
  buildProject,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
} from "@/modules/test-cases/test/utils/project-fixture.util";
import { openSelectOption } from "@/modules/test-cases/test/utils/select-option.util";
import { stubDocumentFonts } from "@/modules/test-cases/test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "@/modules/test-cases/test/utils/stub-scroll-into-view.util";
import { buildTestCaseDetail } from "@/modules/test-cases/test/utils/test-case-fixture.util";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { renderWithReviewer } from "../../test/utils/render-with-reviewer.util";
import {
  buildResolvedComment,
  buildReviewComment,
  OPEN_COMMENT_ID,
} from "../../test/utils/review-comment-fixture.util";
import type { ReviewComment } from "../../typing/types/review-comment.type";
import { ReviewCommentsPanel } from "./review-comments-panel";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("@/modules/test-cases/test/mocks/api-client.mock")).apiClientMock;
});

const COMMENTS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/review-comments";
const RESOLVE_PATH =
  "/api/projects/{project_key}/test-cases/{case_code}/review-comments/{comment_id}/resolve";
const CASE_PATH = { project_key: "SHOP", case_code: "TC-1" };

const { comments } = englishCaseReview;

let storedComments: ReviewComment[] = [];

const respondWithComments = (initial: ReviewComment[]): void => {
  storedComments = initial;
  respondWithRoutes(apiGet, {
    [COMMENTS_PATH]: (): ApiResult => createSuccessResult(storedComments),
  });
};

const renderPanel = (
  options: { detail?: TestCaseDetail; capabilities?: typeof QC_CAPABILITIES } = {},
): ReturnType<typeof renderWithReviewer> => {
  const capabilities = options.capabilities ?? QC_CAPABILITIES;

  return renderWithReviewer(
    <ReviewCommentsPanel
      detail={options.detail ?? buildTestCaseDetail({ status: "in_review" })}
      canComment={capabilities.includes("test_case.edit")}
    />,
    buildProject({ capabilities }),
  );
};

const findSection = async (name: string): Promise<HTMLElement> => {
  return screen.findByRole("region", { name });
};

describe("ReviewCommentsPanel", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
  });

  it("lists open comments, then resolved ones with who resolved them", async () => {
    respondWithComments([buildReviewComment(), buildResolvedComment()]);
    const { container } = renderPanel();

    const open = await findSection(interpolate(comments.openTitle, { count: "1" }));
    expect(within(open).getByText("Say which card number to use.")).toBeInTheDocument();
    expect(within(open).getByText("Rita Reviewer")).toBeInTheDocument();
    expect(within(open).getByText(interpolate(comments.step, { order: "2" }))).toBeInTheDocument();
    expect(
      within(open).getByText(interpolate(comments.version, { number: "2" })),
    ).toBeInTheDocument();

    const resolved = screen.getByRole("region", {
      name: interpolate(comments.resolvedTitle, { count: "1" }),
    });
    expect(within(resolved).getByText(comments.wholeCase)).toBeInTheDocument();
    expect(
      within(resolved).getByText(interpolate(comments.olderVersion, { number: "1" })),
    ).toBeInTheDocument();
    expect(within(resolved).getByText(/^Resolved by Quinn Tester, /)).toBeInTheDocument();
    expect(within(resolved).queryByRole("button", { name: /^Resolve/ })).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("adds a comment on a step of the current version", async () => {
    const user = userEvent.setup();
    respondWithComments([]);
    const added = buildReviewComment({ body: "Name the card." });
    respondWithRoutes(apiPost, {
      [COMMENTS_PATH]: (): ApiResult => {
        storedComments = [added];
        return createCreatedResult(added);
      },
    });
    renderPanel();

    expect(await screen.findByText(comments.emptyTitle)).toBeInTheDocument();
    await user.click(
      await openSelectOption(
        user,
        new RegExp(`^${comments.target}`),
        interpolate(comments.stepOption, { order: "2", action: "Pay as {{data.username}}" }),
      ),
    );
    await user.type(
      screen.getByRole("textbox", { name: new RegExp(`^${comments.body}`) }),
      "  Name the card.  ",
    );
    await user.click(screen.getByRole("button", { name: comments.add }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(COMMENTS_PATH, {
        params: { path: CASE_PATH },
        body: { body: "Name the card.", stepOrder: 2, versionNumber: 2 },
      });
    });
    expect(await screen.findByText(comments.added)).toBeInTheDocument();
    const open = await findSection(interpolate(comments.openTitle, { count: "1" }));
    expect(within(open).getByText("Name the card.")).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: new RegExp(`^${comments.body}`) })).toHaveValue("");
  });

  it("asks for a comment before sending an empty one", async () => {
    const user = userEvent.setup();
    respondWithComments([]);
    renderPanel();

    await user.type(
      await screen.findByRole("textbox", { name: new RegExp(`^${comments.body}`) }),
      "   ",
    );
    await user.click(screen.getByRole("button", { name: comments.add }));

    expect(await screen.findByText(comments.bodyRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("explains a step that is no longer in the current version", async () => {
    const user = userEvent.setup();
    respondWithComments([]);
    respondWithRoutes(apiPost, { [COMMENTS_PATH]: createErrorResult(400, "INVALID_REQUEST") });
    renderPanel();

    await user.type(
      await screen.findByRole("textbox", { name: new RegExp(`^${comments.body}`) }),
      "Check this",
    );
    await user.click(screen.getByRole("button", { name: comments.add }));

    expect(await screen.findByText(comments.errors.stepMissing)).toBeInTheDocument();
  });

  it("resolves an open comment", async () => {
    const user = userEvent.setup();
    respondWithComments([buildReviewComment()]);
    respondWithRoutes(apiPut, {
      [RESOLVE_PATH]: (): ApiResult => {
        const resolved = buildReviewComment({
          isResolved: true,
          resolvedAt: "2026-10-22T11:00:00Z",
          resolvedBy: "b1000000-0000-4000-8000-000000000001",
          resolvedByName: "Quinn Tester",
        });
        storedComments = [resolved];
        return createSuccessResult(resolved);
      },
    });
    renderPanel();

    await user.click(
      await screen.findByRole("button", {
        name: interpolate(comments.resolveLabel, {
          name: "Rita Reviewer",
          target: interpolate(comments.step, { order: "2" }),
        }),
      }),
    );

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(RESOLVE_PATH, {
        params: { path: { ...CASE_PATH, comment_id: OPEN_COMMENT_ID } },
      });
    });
    expect(await screen.findByText(comments.resolved)).toBeInTheDocument();
    expect(
      await findSection(interpolate(comments.resolvedTitle, { count: "1" })),
    ).toBeInTheDocument();
    expect(screen.getByText(comments.emptyTitle)).toBeInTheDocument();
  });

  it("is read-only for roles without test_case.edit", async () => {
    respondWithComments([buildReviewComment()]);
    renderPanel({ capabilities: VIEWER_CAPABILITIES });

    expect(await screen.findByText("Say which card number to use.")).toBeInTheDocument();
    expect(screen.queryByRole("form", { name: comments.formLabel })).toBeNull();
    expect(screen.queryByRole("button", { name: /^Resolve/ })).toBeNull();
  });

  it("takes no new comment on a deprecated case but still resolves open ones", async () => {
    respondWithComments([buildReviewComment()]);
    renderPanel({ detail: buildTestCaseDetail({ status: "deprecated" }) });

    expect(await screen.findByText(comments.deprecated)).toBeInTheDocument();
    expect(screen.queryByRole("form", { name: comments.formLabel })).toBeNull();
    expect(screen.getByRole("button", { name: /^Resolve/ })).toBeInTheDocument();
  });

  it("offers a retry when the comments cannot be loaded", async () => {
    respondWithRoutes(apiGet, { [COMMENTS_PATH]: createErrorResult(429, "RATE_LIMITED") });
    renderPanel();

    expect(await screen.findByText(comments.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishCaseReview.retry })).toBeInTheDocument();
  });
});
