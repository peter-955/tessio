import englishGaps from "@/lib/i18n/locales/en/gaps.json";
import {
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/auth/test/utils/api-result.util";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GapInboxPage } from "./gap-inbox";
import { apiGet, apiPut } from "./test/mocks/api-client.mock";
import { CURRENT_USER_ID, createGap, createResolvedGap } from "./test/utils/gap.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { MAX_INBOX_SIZE } from "./typing/constants/gap.constant";
import type { Gap } from "./typing/types/gap.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("./test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface InboxRequest {
  params: { query: { includeResolved: boolean } };
}

const INBOX_PATH = "/api/gaps/inbox";
const ANSWER_PATH = "/api/projects/{project_key}/gaps/{gap_id}/answer";

const APP_GAP = createGap({
  projectKey: "APP",
  projectName: "Mobile app",
  storyJiraKey: "APP-1",
  storyTitle: "Sign in with a passkey",
  question: "Which devices must support passkeys?",
});
const SHOP_GAP = createGap({
  id: "b1000000-0000-4000-8000-000000000002",
  question: "Which cards are accepted?",
});

const { inbox, actions } = englishGaps;

const respondWithInbox = (gaps: Gap[] | ((isIncludingResolved: boolean) => Gap[])): void => {
  apiGet.mockImplementation((path, options): Promise<ApiResult> => {
    if (path !== INBOX_PATH) {
      return Promise.reject(new Error(`No mocked response for ${path}`));
    }

    const isIncludingResolved = (options as InboxRequest).params.query.includeResolved;

    return Promise.resolve(
      createSuccessResult(typeof gaps === "function" ? gaps(isIncludingResolved) : gaps),
    );
  });
};

const readInboxQueries = (): boolean[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === INBOX_PATH;
    })
    .map(([, options]) => {
      return (options as InboxRequest).params.query.includeResolved;
    });
};

const findCards = async (): Promise<HTMLElement[]> => {
  const list = await screen.findByRole("list", { name: englishGaps.tab.listLabel });

  return within(list).getAllByRole("listitem");
};

describe("GapInboxPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    respondWithInbox([APP_GAP, SHOP_GAP]);
  });

  it("lists open gaps first, then all gaps after switching the filter", async () => {
    const user = userEvent.setup();
    const resolvedGap = createResolvedGap({ raisedBy: CURRENT_USER_ID });
    respondWithInbox((isIncludingResolved) => {
      return isIncludingResolved ? [APP_GAP, SHOP_GAP, resolvedGap] : [APP_GAP, SHOP_GAP];
    });
    const { container } = renderWithProviders(<GapInboxPage />);

    expect(screen.getByRole("heading", { name: inbox.title })).toBeInTheDocument();
    expect(await findCards()).toHaveLength(2);
    expect(readInboxQueries()).toEqual([false]);

    await user.click(screen.getByRole("radio", { name: inbox.filterAll }));

    await waitFor(async () => {
      expect(await findCards()).toHaveLength(3);
    });
    expect(readInboxQueries()).toEqual([false, true]);
    expect(screen.getByRole("button", { name: actions.reopen })).toBeInTheDocument();
    expect(screen.queryByText(/most recent/)).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the project and links to the story gaps tab", async () => {
    renderWithProviders(<GapInboxPage />);

    const card = within((await findCards())[0]);
    expect(card.getByText("Mobile app")).toBeInTheDocument();
    expect(card.getByRole("link", { name: "APP-1 · Sign in with a passkey" })).toHaveAttribute(
      "href",
      "/projects/APP/stories/APP-1?tab=gaps",
    );
    expect(card.getByRole("button", { name: actions.answer })).toBeInTheDocument();
    expect(card.getByRole("button", { name: actions.reassign })).toBeInTheDocument();
  });

  it("answers a gap of another project", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createSuccessResult(createResolvedGap({ id: APP_GAP.id })));
    renderWithProviders(<GapInboxPage />);

    const card = within((await findCards())[0]);
    await user.click(card.getByRole("button", { name: actions.answer }));
    const dialog = await screen.findByRole("dialog", { name: englishGaps.answer.title });
    await user.type(within(dialog).getByRole("textbox", { name: /Your answer/ }), "iOS 17+");
    await user.click(within(dialog).getByRole("button", { name: englishGaps.answer.submit }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(ANSWER_PATH, {
        params: { path: { project_key: "APP", gap_id: APP_GAP.id } },
        body: { answer: "iOS 17+" },
      });
    });
    expect(await screen.findByText(englishGaps.toasts.answered)).toBeInTheDocument();
    await waitFor(() => {
      expect(readInboxQueries()).toHaveLength(2);
    });
  });

  it("shows the empty state", async () => {
    respondWithRoutes(apiGet, { [INBOX_PATH]: createSuccessResult([]) });
    const { container } = renderWithProviders(<GapInboxPage />);

    expect(await screen.findByText(inbox.emptyTitle)).toBeInTheDocument();
    expect(screen.getByText(inbox.emptyDescription)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("says when only the most recent gaps are shown", async () => {
    const gaps = Array.from({ length: MAX_INBOX_SIZE }, (_, index): Gap => {
      return createGap({
        id: `b1000000-0000-4000-8000-${String(index).padStart(12, "0")}`,
        question: `Question ${index}`,
      });
    });
    respondWithRoutes(apiGet, { [INBOX_PATH]: createSuccessResult(gaps) });
    renderWithProviders(<GapInboxPage />);

    expect(await screen.findByText("Showing the 200 most recent gaps.")).toBeInTheDocument();
  });
});
