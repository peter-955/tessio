import englishCaseReview from "@/lib/i18n/locales/en/caseReview.json";
import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import { TestCaseAlerts } from "@/modules/test-cases/components/test-case-alerts/test-case-alerts";
import { TestCaseStatusActions } from "@/modules/test-cases/components/test-case-status-actions/test-case-status-actions";
import { apiGet } from "@/modules/test-cases/test/mocks/api-client.mock";
import {
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/test-cases/test/utils/api-result.util";
import { interpolate } from "@/modules/test-cases/test/utils/interpolate.util";
import {
  buildProject,
  QC_CAPABILITIES,
} from "@/modules/test-cases/test/utils/project-fixture.util";
import { buildTestCaseDetail } from "@/modules/test-cases/test/utils/test-case-fixture.util";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi, type Mock } from "vitest";
import { axe } from "vitest-axe";
import { buildCurrentUser } from "../../test/utils/current-user-fixture.util";
import { renderWithReviewer } from "../../test/utils/render-with-reviewer.util";
import {
  buildResolvedComment,
  buildReviewComment,
  REVIEWER_ID,
} from "../../test/utils/review-comment-fixture.util";
import type { ReviewComment } from "../../typing/types/review-comment.type";
import { ReviewStatusNotice } from "./review-status-notice";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("@/modules/test-cases/test/mocks/api-client.mock")).apiClientMock;
});

const COMMENTS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/review-comments";

const { notice } = englishCaseReview;

const { actions } = englishTestCases;

interface Options {
  comments?: ReviewComment[];
  detail?: TestCaseDetail;
  isSeparateReviewerRequired?: boolean;
  userId?: string;
  onShowComments?: Mock<() => void>;
}

const renderGates = ({
  comments = [],
  detail = buildTestCaseDetail({ status: "in_review" }),
  isSeparateReviewerRequired = false,
  userId = REVIEWER_ID,
  onShowComments = vi.fn<() => void>(),
}: Options = {}): ReturnType<typeof renderWithReviewer> => {
  respondWithRoutes(apiGet, { [COMMENTS_PATH]: createSuccessResult(comments) });

  return renderWithReviewer(
    <>
      <TestCaseStatusActions detail={detail} isDirty={false} />
      <TestCaseAlerts detail={detail} canEdit />
      <ReviewStatusNotice detail={detail} canEdit onShowComments={onShowComments} />
    </>,
    buildProject({
      capabilities: QC_CAPABILITIES,
      requireSeparateReviewer: isSeparateReviewerRequired,
    }),
    buildCurrentUser({ id: userId }),
  );
};

describe("review gates on the case", () => {
  beforeEach(() => {
    apiGet.mockReset();
  });

  it("blocks Mark ready while a review comment is open and links to the comments", async () => {
    const user = userEvent.setup();
    const onShowComments = vi.fn<() => void>();
    const { container } = renderGates({
      comments: [buildReviewComment(), buildResolvedComment()],
      onShowComments,
    });

    expect(
      await screen.findByText(interpolate(notice.openComments_one, { count: "1" })),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: actions.markReady })).toBeDisabled();
    expect(screen.getByRole("button", { name: actions.markReady })).toHaveAttribute(
      "title",
      notice.resolveFirst,
    );

    await user.click(screen.getByRole("button", { name: notice.showComments }));
    expect(onShowComments).toHaveBeenCalledOnce();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("allows Mark ready once every comment is resolved", async () => {
    renderGates({ comments: [buildResolvedComment()] });

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalled();
    });
    expect(await screen.findByRole("button", { name: actions.markReady })).toBeEnabled();
    expect(screen.queryByText(/review comments? (is|are) open/)).toBeNull();
  });

  it("hides Mark ready and Mark reviewed from the author when the project needs another reviewer", async () => {
    const detail = buildTestCaseDetail({ status: "in_review", needsReview: true });
    renderGates({
      detail,
      isSeparateReviewerRequired: true,
      userId: detail.currentVersion.createdBy,
    });

    expect(
      await screen.findByText(interpolate(notice.separateReviewer, { number: "2" })),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.markReady })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.markReviewed })).toBeNull();
    expect(screen.getByRole("button", { name: actions.more })).toBeInTheDocument();
  });

  it("keeps both actions for another reviewer when the setting is on", async () => {
    renderGates({
      detail: buildTestCaseDetail({ status: "in_review", needsReview: true }),
      isSeparateReviewerRequired: true,
    });

    expect(await screen.findByRole("button", { name: actions.markReady })).toBeEnabled();
    expect(screen.getByRole("button", { name: actions.markReviewed })).toBeInTheDocument();
    expect(screen.queryByText(interpolate(notice.separateReviewer, { number: "2" }))).toBeNull();
  });

  it("lets the author review their own case when the setting is off", async () => {
    const detail = buildTestCaseDetail({ status: "in_review" });
    renderGates({ detail, userId: detail.currentVersion.createdBy });

    expect(await screen.findByRole("button", { name: actions.markReady })).toBeEnabled();
  });
});
