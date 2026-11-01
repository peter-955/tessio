import englishGaps from "@/lib/i18n/locales/en/gaps.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { buildCriterion, buildStoryDetail } from "@/modules/stories/test/utils/story-fixture.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import { ASSIGNEE_ID, createGap, createMember } from "../../test/utils/gap.fixture";
import { chooseSelectOption, readSelectOptionNames } from "../../test/utils/select-option.util";
import { stubDocumentFonts } from "../../test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { RaiseGapModal } from "./raise-gap-modal";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const MEMBERS_PATH = "/api/projects/{project_key}/members";
const TEST_CASES_PATH = "/api/projects/{project_key}/test-cases";
const RAISE_PATH = "/api/projects/{project_key}/stories/{jira_key}/gaps";

const STORY = buildStoryDetail({
  criteria: [
    buildCriterion(),
    buildCriterion({
      id: "d1000000-0000-4000-8000-000000000002",
      code: "AC-2",
      position: 2,
      text: "Declined card shows an error",
    }),
    buildCriterion({
      id: "d1000000-0000-4000-8000-000000000003",
      code: "AC-3",
      position: 3,
      text: "Old rule",
      isRemoved: true,
      removedAt: "2026-10-18T09:00:00Z",
    }),
  ],
});

const TEST_CASES = [
  {
    id: "e1000000-0000-4000-8000-000000000004",
    code: "TC-4",
    storyId: STORY.id,
    storyKey: "SHOP-1",
    title: "Refund in euros",
    priority: "medium",
    status: "ready",
    currentVersionId: "f1000000-0000-4000-8000-000000000004",
    currentVersionNumber: 1,
    stepCount: 3,
    criterionIds: [],
    needsReview: false,
    needsReviewAt: null,
    lastSavedAt: "2026-10-20T09:00:00Z",
  },
];

const { raise, target, type: typeLabels, dataScope, errors, toasts } = englishGaps;

const renderModal = (): { onClose: () => void; container: HTMLElement } => {
  const onClose = vi.fn<() => void>();
  const { container } = renderWithProviders(
    <RaiseGapModal projectKey="SHOP" jiraKey="SHOP-1" onClose={onClose} />,
  );

  return { onClose, container };
};

const findDialog = (): Promise<HTMLElement> => {
  return screen.findByRole("dialog", { name: raise.title });
};

const fillQuestion = async (user: UserEvent, question: string): Promise<void> => {
  await user.type(screen.getByRole("textbox", { name: /^Question/ }), question);
};

const submit = async (user: UserEvent): Promise<void> => {
  const dialog = await findDialog();
  await user.click(within(dialog).getByRole("button", { name: raise.submit }));
};

describe("RaiseGapModal", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    respondWithRoutes(apiGet, {
      [STORY_PATH]: createSuccessResult(STORY),
      [MEMBERS_PATH]: createSuccessResult([
        createMember(),
        createMember({
          userId: "a1000000-0000-4000-8000-000000000010",
          name: "Vi Viewer",
          role: "viewer",
        }),
      ]),
      [TEST_CASES_PATH]: createSuccessResult(TEST_CASES),
    });
    apiPost.mockResolvedValue(createSuccessResult(createGap()));
  });

  it("raises a story gap without a target ref, toasts and closes", async () => {
    const user = userEvent.setup();
    const { onClose } = renderModal();

    await findDialog();
    await chooseSelectOption(user, /^Type/, typeLabels.unclear_goal);
    await fillQuestion(user, "  Which cards are accepted?  ");
    await submit(user);

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(RAISE_PATH, {
        params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
        body: {
          type: "unclear_goal",
          severity: "medium",
          targetType: "story",
          question: "Which cards are accepted?",
          assigneeId: null,
        },
      });
    });
    expect(await screen.findByText(toasts.raised)).toBeInTheDocument();
    expect(onClose).toHaveBeenCalled();
  });

  it("lists only the criteria that are not removed", async () => {
    const user = userEvent.setup();
    const { container } = renderModal();

    await findDialog();
    expect(screen.queryByRole("combobox", { name: /^Which one/ })).not.toBeInTheDocument();
    await user.click(screen.getByRole("radio", { name: target.criterion }));

    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Which one/ })).toBeEnabled();
    });
    expect(await readSelectOptionNames(user, /^Which one/)).toEqual([
      "AC-1 · Card payment succeeds",
      "AC-2 · Declined card shows an error",
    ]);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("loads the test case options of the story", async () => {
    const user = userEvent.setup();
    renderModal();

    await findDialog();
    expect(
      apiGet.mock.calls.some(([path]) => {
        return path === TEST_CASES_PATH;
      }),
    ).toBe(false);
    await user.click(screen.getByRole("radio", { name: target.test_case }));

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith(TEST_CASES_PATH, {
        params: { path: { project_key: "SHOP" }, query: { storyKey: "SHOP-1" } },
        signal: expect.any(AbortSignal),
      });
    });
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Which one/ })).toBeEnabled();
    });
    expect(await readSelectOptionNames(user, /^Which one/)).toEqual(["TC-4 · Refund in euros"]);
  });

  it("says when there is nothing to pick", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [STORY_PATH]: createSuccessResult(STORY),
      [MEMBERS_PATH]: createSuccessResult([]),
      [TEST_CASES_PATH]: createSuccessResult([]),
    });
    renderModal();

    await findDialog();
    await user.click(screen.getByRole("radio", { name: target.test_case }));

    expect(await screen.findByText(raise.noTargets)).toBeInTheDocument();
  });

  it("shows the data scope only for missing test data", async () => {
    const user = userEvent.setup();
    renderModal();

    await findDialog();
    await chooseSelectOption(user, /^Type/, typeLabels.missing_ac);
    expect(screen.queryByRole("combobox", { name: dataScope.label })).not.toBeInTheDocument();

    await chooseSelectOption(user, /^Type/, typeLabels.missing_test_data);
    expect(screen.getByRole("combobox", { name: dataScope.label })).toBeInTheDocument();

    await chooseSelectOption(user, /^Type/, typeLabels.other);
    expect(screen.queryByRole("combobox", { name: dataScope.label })).not.toBeInTheDocument();
  });

  it("blocks the submit without a type, a question or a target", async () => {
    const user = userEvent.setup();
    renderModal();

    await findDialog();
    await user.click(screen.getByRole("radio", { name: target.criterion }));
    await fillQuestion(user, "   ");
    await submit(user);

    expect(await screen.findByText(errors.questionRequired)).toBeInTheDocument();
    expect(screen.getByText(errors.typeRequired)).toBeInTheDocument();
    expect(screen.getByText(errors.targetRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows an unknown reference on the target field", async () => {
    const user = userEvent.setup();
    apiPost.mockResolvedValue(createErrorResult(422, "UNKNOWN_REFERENCE"));
    const { onClose } = renderModal();

    await findDialog();
    await chooseSelectOption(user, /^Type/, typeLabels.missing_ac);
    await user.click(screen.getByRole("radio", { name: target.criterion }));
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Which one/ })).toBeEnabled();
    });
    await chooseSelectOption(user, /^Which one/, "AC-2 · Declined card shows an error");
    await fillQuestion(user, "Is this still valid?");
    await submit(user);

    expect(await screen.findByText(errors.unknownTarget)).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: /^Which one/ })).toHaveAccessibleDescription(
      errors.unknownTarget,
    );
    expect(onClose).not.toHaveBeenCalled();
  });

  it("shows an inactive assignee on the assignee field", async () => {
    const user = userEvent.setup();
    apiPost.mockResolvedValue(createErrorResult(409, "ASSIGNEE_NOT_ACTIVE_MEMBER"));
    renderModal();

    await findDialog();
    await chooseSelectOption(user, /^Type/, typeLabels.other);
    await fillQuestion(user, "Who decides?");
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: raise.assigneeLabel })).toBeInTheDocument();
    });
    await chooseSelectOption(user, raise.assigneeLabel, "Bao Ba · BA");
    await submit(user);

    expect(await screen.findByText(errors.assigneeNotActive)).toBeInTheDocument();
  });

  it("sends the exact request for a test case gap", async () => {
    const user = userEvent.setup();
    renderModal();

    await findDialog();
    expect(await readSelectOptionNames(user, raise.assigneeLabel)).toEqual(["Bao Ba · BA"]);
    await user.keyboard("{Escape}");
    await chooseSelectOption(user, /^Type/, typeLabels.missing_test_data);
    await user.click(screen.getByRole("radio", { name: englishGaps.severity.high }));
    await user.click(screen.getByRole("radio", { name: target.test_case }));
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Which one/ })).toBeEnabled();
    });
    await chooseSelectOption(user, /^Which one/, "TC-4 · Refund in euros");
    await chooseSelectOption(user, dataScope.label, dataScope.environment);
    await fillQuestion(user, "Which IBAN should the refund use?");
    await chooseSelectOption(user, raise.assigneeLabel, "Bao Ba · BA");
    await submit(user);

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledTimes(1);
    });
    expect(apiPost.mock.calls[0][1]).toStrictEqual({
      params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
      body: {
        type: "missing_test_data",
        severity: "high",
        targetType: "test_case",
        targetRef: "TC-4",
        dataScope: "environment",
        question: "Which IBAN should the refund use?",
        assigneeId: ASSIGNEE_ID,
      },
    });
  });
});
