import {
  VIEWER_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import type {
  ProjectCapability,
  ProjectRole,
} from "@/components/project-context/typing/types/project.type";
import englishGaps from "@/lib/i18n/locales/en/gaps.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost, apiPut } from "../../test/mocks/api-client.mock";
import {
  CURRENT_USER_ID,
  createGap,
  createMember,
  createResolvedGap,
} from "../../test/utils/gap.fixture";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { chooseSelectOption } from "../../test/utils/select-option.util";
import { stubDocumentFonts } from "../../test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import type { Gap } from "../../typing/types/gap.type";
import { StoryGaps } from "./story-gaps";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("../../test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const GAPS_PATH = "/api/projects/{project_key}/gaps";
const MEMBERS_PATH = "/api/projects/{project_key}/members";
const ANSWER_PATH = "/api/projects/{project_key}/gaps/{gap_id}/answer";
const REOPEN_PATH = "/api/projects/{project_key}/gaps/{gap_id}/reopen";
const ASSIGNEE_PATH = "/api/projects/{project_key}/gaps/{gap_id}/assignee";
const QC_ID = "a1000000-0000-4000-8000-000000000012";

const WRITER_CAPABILITIES: ProjectCapability[] = [
  ...VIEWER_CAPABILITIES,
  "gap.raise",
  "gap.answer",
  "gap.reassign",
];

const OPEN_GAP = createGap();
const SECOND_OPEN_GAP = createGap({
  id: "b1000000-0000-4000-8000-000000000002",
  question: "What happens on a declined card?",
});
const RESOLVED_GAP = createResolvedGap();

const { actions, errors, toasts } = englishGaps;

const countRequests = (path: string): number => {
  return apiGet.mock.calls.filter(([calledPath]) => {
    return calledPath === path;
  }).length;
};

const respondWithGaps = (gaps: Gap[] | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [GAPS_PATH]: typeof gaps === "function" ? gaps : createSuccessResult(gaps),
    [MEMBERS_PATH]: createSuccessResult([
      createMember(),
      createMember({ userId: QC_ID, name: "Quinn Qc", role: "qc", email: "quinn@example.test" }),
    ]),
  });
};

const renderTab = (
  capabilities: ProjectCapability[] = WRITER_CAPABILITIES,
  myRole: ProjectRole = "dev",
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<StoryGaps jiraKey="SHOP-1" />, buildProject({ capabilities, myRole }));
};

const findCards = async (): Promise<HTMLElement[]> => {
  const list = await screen.findByRole("list", { name: englishGaps.tab.listLabel });

  return within(list).getAllByRole("listitem");
};

const findCardByQuestion = async (question: string): Promise<HTMLElement> => {
  const text = await screen.findByText(question);
  const card = text.closest("li");
  if (card === null) {
    throw new Error("The gap card is not rendered.");
  }

  return card;
};

describe("StoryGaps", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    respondWithGaps([OPEN_GAP, RESOLVED_GAP, SECOND_OPEN_GAP]);
  });

  it("shows the banner, filters by status and shows the answer", async () => {
    const user = userEvent.setup();
    const { container } = renderTab();

    expect(await screen.findByText("2 open gaps block runs")).toBeInTheDocument();
    expect(screen.getByText(englishGaps.banner.description)).toBeInTheDocument();
    expect(apiGet).toHaveBeenCalledWith(GAPS_PATH, {
      params: { path: { project_key: "SHOP" }, query: { storyKey: "SHOP-1" } },
      signal: expect.any(AbortSignal),
    });
    expect(countRequests(GAPS_PATH)).toBe(1);
    expect(screen.getByRole("radio", { name: "Open (2)" })).toBeChecked();
    expect(await findCards()).toHaveLength(2);

    await user.click(screen.getByRole("radio", { name: "Answered (1)" }));

    const cards = await findCards();
    expect(cards).toHaveLength(1);
    const resolvedCard = within(cards[0]);
    expect(resolvedCard.getByText(RESOLVED_GAP.question)).toBeInTheDocument();
    expect(resolvedCard.getByText(/Yes, Amex is accepted\./)).toBeInTheDocument();
    expect(resolvedCard.getByText(/Answered by Bao Ba/)).toBeInTheDocument();
    expect(resolvedCard.getByText(englishGaps.status.resolved)).toBeInTheDocument();

    await user.click(screen.getByRole("radio", { name: "All (3)" }));
    expect(await findCards()).toHaveLength(3);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("hides the banner and shows the empty state when nothing is open", async () => {
    const user = userEvent.setup();
    respondWithGaps([RESOLVED_GAP]);
    renderTab();

    expect(await screen.findByText(englishGaps.empty.openTitle)).toBeInTheDocument();
    expect(screen.getByText(englishGaps.empty.openDescription)).toBeInTheDocument();
    expect(screen.queryByText(/block runs/)).not.toBeInTheDocument();

    respondWithGaps([]);
    await user.click(screen.getByRole("radio", { name: "Answered (1)" }));
    expect(await findCards()).toHaveLength(1);
  });

  it("shows the empty texts of the answered and all filters", async () => {
    const user = userEvent.setup();
    respondWithGaps([]);
    renderTab();

    expect(await screen.findByText(englishGaps.empty.openTitle)).toBeInTheDocument();
    await user.click(screen.getByRole("radio", { name: "Answered (0)" }));
    expect(screen.getByText(englishGaps.empty.resolvedTitle)).toBeInTheDocument();
    await user.click(screen.getByRole("radio", { name: "All (0)" }));
    expect(screen.getByText(englishGaps.empty.allTitle)).toBeInTheDocument();
  });

  it("shows the Claude, deactivated, role and target badges", async () => {
    respondWithGaps([
      createGap({
        isRaisedViaClaude: true,
        targetType: "criterion",
        targetRef: "AC-2",
        severity: "high",
        type: "missing_ac",
      }),
      createGap({
        id: "b1000000-0000-4000-8000-000000000003",
        question: "Which test card number?",
        targetType: "test_case",
        targetRef: "TC-4",
        type: "missing_test_data",
        dataScope: "environment",
        assigneeStatus: "deactivated",
        assigneeName: "Dee Gone",
      }),
      createGap({
        id: "b1000000-0000-4000-8000-000000000004",
        question: "Who signs off refunds?",
        assigneeId: null,
        assigneeName: null,
        assigneeStatus: null,
        assigneeRole: "ba",
      }),
      createGap({
        id: "b1000000-0000-4000-8000-000000000005",
        question: "Is there a limit?",
        assigneeId: null,
        assigneeName: null,
        assigneeStatus: null,
      }),
    ]);
    const { container } = renderTab();

    const claudeCard = within(await findCardByQuestion(OPEN_GAP.question));
    expect(claudeCard.getByText(englishGaps.badge.viaClaude)).toBeInTheDocument();
    expect(claudeCard.getByText("AC-2")).toBeInTheDocument();
    expect(claudeCard.getByText(englishGaps.severity.high)).toBeInTheDocument();
    expect(claudeCard.getByText(englishGaps.type.missing_ac)).toBeInTheDocument();
    expect(claudeCard.getByText(/Raised by Quinn Qc/)).toBeInTheDocument();
    expect(claudeCard.getByText("Assigned to Bao Ba")).toBeInTheDocument();
    expect(claudeCard.queryByText(englishGaps.badge.deactivated)).not.toBeInTheDocument();

    const deactivatedCard = within(await findCardByQuestion("Which test card number?"));
    expect(deactivatedCard.getByText("TC-4")).toBeInTheDocument();
    expect(deactivatedCard.getByText(englishGaps.badge.deactivated)).toBeInTheDocument();
    expect(deactivatedCard.getByText(englishGaps.card.reassignHint)).toBeInTheDocument();
    expect(deactivatedCard.getByText(/Data scope: Environment data/)).toBeInTheDocument();
    expect(deactivatedCard.queryByText(englishGaps.badge.viaClaude)).not.toBeInTheDocument();

    const roleCard = within(await findCardByQuestion("Who signs off refunds?"));
    expect(roleCard.getByText("Assigned to any BA")).toBeInTheDocument();
    expect(roleCard.getByText(englishGaps.target.story)).toBeInTheDocument();

    const unassignedCard = within(await findCardByQuestion("Is there a limit?"));
    expect(unassignedCard.getByText(englishGaps.card.unassigned)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows no action to a viewer", async () => {
    const user = userEvent.setup();
    respondWithGaps([OPEN_GAP, createResolvedGap({ raisedBy: CURRENT_USER_ID })]);
    renderTab(VIEWER_CAPABILITIES, "viewer");

    expect(await findCards()).toHaveLength(1);
    await user.click(screen.getByRole("radio", { name: "All (2)" }));
    expect(await findCards()).toHaveLength(2);
    for (const label of [actions.raise, actions.answer, actions.reassign, actions.reopen]) {
      expect(screen.queryByRole("button", { name: label })).not.toBeInTheDocument();
    }
  });

  it("answers a gap with the trimmed text, then toasts and refetches", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createSuccessResult(createResolvedGap({ id: OPEN_GAP.id })));
    renderTab();

    const card = within(await findCardByQuestion(OPEN_GAP.question));
    await user.click(card.getByRole("button", { name: actions.answer }));
    const dialog = await screen.findByRole("dialog", { name: englishGaps.answer.title });
    const submit = within(dialog).getByRole("button", { name: englishGaps.answer.submit });
    expect(submit).toBeDisabled();
    expect(within(dialog).getByText(OPEN_GAP.question)).toBeInTheDocument();

    await user.type(
      within(dialog).getByRole("textbox", { name: /Your answer/ }),
      "  Visa and Mastercard only.  ",
    );
    await user.click(submit);

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(ANSWER_PATH, {
        params: { path: { project_key: "SHOP", gap_id: OPEN_GAP.id } },
        body: { answer: "Visa and Mastercard only." },
      });
    });
    expect(await screen.findByText(toasts.answered)).toBeInTheDocument();
    await waitFor(() => {
      expect(countRequests(GAPS_PATH)).toBe(2);
    });
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  it("explains an already answered gap, closes and refetches", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createErrorResult(409, "GAP_NOT_OPEN"));
    renderTab();

    const card = within(await findCardByQuestion(OPEN_GAP.question));
    await user.click(card.getByRole("button", { name: actions.answer }));
    const dialog = await screen.findByRole("dialog", { name: englishGaps.answer.title });
    await user.type(within(dialog).getByRole("textbox", { name: /Your answer/ }), "Visa");
    await user.click(within(dialog).getByRole("button", { name: englishGaps.answer.submit }));

    expect(await screen.findByText(errors.alreadyResolved)).toBeInTheDocument();
    await waitFor(() => {
      expect(countRequests(GAPS_PATH)).toBe(2);
    });
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  it("offers reopen to the raiser and to qc, not to another dev", async () => {
    const ownGap = createResolvedGap({ raisedBy: CURRENT_USER_ID, question: "Own question?" });
    const otherGap = createResolvedGap({
      id: "b1000000-0000-4000-8000-000000000098",
      question: "Other question?",
    });
    respondWithGaps([ownGap, otherGap]);
    const user = userEvent.setup();
    const { unmount } = renderTab(WRITER_CAPABILITIES, "dev");

    await user.click(await screen.findByRole("radio", { name: "Answered (2)" }));
    const ownCard = within(await findCardByQuestion("Own question?"));
    const otherCard = within(await findCardByQuestion("Other question?"));
    expect(ownCard.getByRole("button", { name: actions.reopen })).toBeInTheDocument();
    expect(otherCard.queryByRole("button", { name: actions.reopen })).not.toBeInTheDocument();
    expect(ownCard.queryByRole("button", { name: actions.answer })).not.toBeInTheDocument();
    unmount();

    apiPost.mockResolvedValue(createSuccessResult(createGap({ id: otherGap.id })));
    renderTab(WRITER_CAPABILITIES, "qc");
    await user.click(await screen.findByRole("radio", { name: "Answered (2)" }));
    const qcCard = within(await findCardByQuestion("Other question?"));
    await user.click(qcCard.getByRole("button", { name: actions.reopen }));
    const dialog = await screen.findByRole("dialog", { name: englishGaps.reopen.title });
    expect(within(dialog).getByText(englishGaps.reopen.description)).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: englishGaps.reopen.submit }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(REOPEN_PATH, {
        params: { path: { project_key: "SHOP", gap_id: otherGap.id } },
      });
    });
    expect(await screen.findByText(toasts.reopened)).toBeInTheDocument();
  });

  it("explains a gap that is already open again", async () => {
    const user = userEvent.setup();
    respondWithGaps([createResolvedGap({ raisedBy: CURRENT_USER_ID })]);
    apiPost.mockResolvedValue(createErrorResult(409, "INVALID_STATUS_TRANSITION"));
    renderTab();

    await user.click(await screen.findByRole("radio", { name: "Answered (1)" }));
    await user.click(await screen.findByRole("button", { name: actions.reopen }));
    const dialog = await screen.findByRole("dialog", { name: englishGaps.reopen.title });
    await user.click(within(dialog).getByRole("button", { name: englishGaps.reopen.submit }));

    expect(await screen.findByText(errors.alreadyOpen)).toBeInTheDocument();
  });

  it("reassigns to a member or a role and shows an inactive member inline", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createSuccessResult(OPEN_GAP));
    renderTab();

    const openReassign = async (): Promise<HTMLElement> => {
      const card = within(await findCardByQuestion(OPEN_GAP.question));
      await user.click(card.getByRole("button", { name: actions.reassign }));

      return screen.findByRole("dialog", { name: englishGaps.reassign.title });
    };

    let dialog = await openReassign();
    await waitFor(() => {
      expect(within(dialog).getByRole("combobox", { name: /Assign to/ })).toHaveValue(
        "Bao Ba · BA",
      );
    });
    await chooseSelectOption(user, /Assign to/, "Quinn Qc · QC");
    await user.click(within(dialog).getByRole("button", { name: englishGaps.reassign.submit }));
    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(ASSIGNEE_PATH, {
        params: { path: { project_key: "SHOP", gap_id: OPEN_GAP.id } },
        body: { assigneeId: QC_ID },
      });
    });
    expect(await screen.findByText(toasts.reassigned)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    dialog = await openReassign();
    await chooseSelectOption(user, /Assign to/, "Any QC");
    await user.click(within(dialog).getByRole("button", { name: englishGaps.reassign.submit }));
    await waitFor(() => {
      expect(apiPut).toHaveBeenLastCalledWith(ASSIGNEE_PATH, {
        params: { path: { project_key: "SHOP", gap_id: OPEN_GAP.id } },
        body: { assigneeRole: "qc" },
      });
    });
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    apiPut.mockResolvedValue(createErrorResult(409, "ASSIGNEE_NOT_ACTIVE_MEMBER"));
    const membersRequestsBefore = countRequests(MEMBERS_PATH);
    dialog = await openReassign();
    await chooseSelectOption(user, /Assign to/, "Quinn Qc · QC");
    await user.click(within(dialog).getByRole("button", { name: englishGaps.reassign.submit }));

    expect(await within(dialog).findByText(errors.assigneeNotActive)).toBeInTheDocument();
    await waitFor(() => {
      expect(countRequests(MEMBERS_PATH)).toBeGreaterThan(membersRequestsBefore);
    });
    expect(screen.getByRole("dialog", { name: englishGaps.reassign.title })).toBeInTheDocument();
  });

  it("retries after a load error", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respondWithGaps(() => {
      return isFailing
        ? createErrorResult(500, "INVALID_REQUEST")
        : createSuccessResult([OPEN_GAP]);
    });
    const { container } = renderTab();

    expect(await screen.findByText(englishGaps.loadError)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishGaps.retry }));

    expect(await findCards()).toHaveLength(1);
    expect(screen.getByText("1 open gap blocks runs")).toBeInTheDocument();
  });

  it("shows the loading skeleton and no banner while loading", () => {
    apiGet.mockReturnValue(
      new Promise<ApiResult>(() => {
        return;
      }),
    );
    renderTab();

    expect(screen.getByRole("status", { name: englishGaps.loading })).toHaveAttribute(
      "aria-busy",
      "true",
    );
    expect(screen.queryByText(/block runs/)).not.toBeInTheDocument();
  });
});
