import englishNotificationPreferences from "@/lib/i18n/locales/en/notificationPreferences.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/auth/test/utils/api-result.util";
import { renderSignedIn } from "@/modules/profile/test/utils/render-signed-in.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPatch } from "../../test/mocks/api-client.mock";
import { buildDefaultNotificationPreferences } from "../../test/utils/notification-preference-fixture.util";
import type { NotificationPreference } from "../../typing/types/notification-preference.type";
import { NotificationPreferencesCard } from "./notification-preferences-card";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const PREFERENCES_PATH = "/api/me/notification-preferences";

const { card, kinds } = englishNotificationPreferences;

const inAppName = (kind: string): string => {
  return card.inAppFor.replace("{{kind}}", kind);
};

const emailName = (kind: string): string => {
  return card.emailFor.replace("{{kind}}", kind);
};

describe("NotificationPreferencesCard", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPatch.mockReset();
    respondWithRoutes(apiGet, {
      [PREFERENCES_PATH]: createSuccessResult(buildDefaultNotificationPreferences()),
    });
  });

  it("shows each kind with its in-app and email settings", async () => {
    const { container } = renderSignedIn(<NotificationPreferencesCard />);

    expect(screen.getByRole("heading", { name: card.title })).toBeInTheDocument();
    expect(
      screen.getByText(card.description.replace("{{email}}", "ada@example.test")),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("checkbox", { name: emailName(kinds.gapAssigned.title) }),
    ).toBeChecked();
    expect(
      screen.getByRole("checkbox", { name: emailName(kinds.failureAssigned.title) }),
    ).toBeChecked();
    expect(
      screen.getByRole("checkbox", { name: emailName(kinds.runFinished.title) }),
    ).not.toBeChecked();
    expect(
      screen.getByRole("checkbox", { name: emailName(kinds.reportReady.title) }),
    ).not.toBeChecked();
    expect(
      screen.getByRole("checkbox", { name: inAppName(kinds.suiteRunFinished.title) }),
    ).toBeChecked();
    expect(screen.getAllByRole("checkbox")).toHaveLength(10);
    expect(screen.getByRole("button", { name: card.save })).toBeDisabled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("saves only the changed kinds and fields", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [PREFERENCES_PATH]: (): ApiResult => {
        const body = (
          apiPatch.mock.calls.at(-1)?.[1] as {
            body: { preferences: Partial<NotificationPreference>[] };
          }
        ).body;
        const saved = buildDefaultNotificationPreferences().map((preference) => {
          const change = body.preferences.find((candidate) => candidate.kind === preference.kind);
          return { ...preference, ...change };
        });
        return createSuccessResult(saved);
      },
    });
    renderSignedIn(<NotificationPreferencesCard />);

    await user.click(
      await screen.findByRole("checkbox", { name: emailName(kinds.runFinished.title) }),
    );
    await user.click(screen.getByRole("checkbox", { name: inAppName(kinds.gapAssigned.title) }));
    const save = screen.getByRole("button", { name: card.save });
    expect(save).toBeEnabled();
    await user.click(save);

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(PREFERENCES_PATH, {
        body: {
          preferences: [
            { kind: "gap_assigned", inApp: false },
            { kind: "run_finished", email: true },
          ],
        },
      });
    });
    expect(await screen.findByText(card.saved)).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: emailName(kinds.runFinished.title) }),
    ).toBeChecked();
    expect(
      screen.getByRole("checkbox", { name: inAppName(kinds.gapAssigned.title) }),
    ).not.toBeChecked();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: card.save })).toBeDisabled();
    });
  });

  it("does not save when a change is undone", async () => {
    const user = userEvent.setup();
    renderSignedIn(<NotificationPreferencesCard />);

    const reportEmail = await screen.findByRole("checkbox", {
      name: emailName(kinds.reportReady.title),
    });
    await user.click(reportEmail);
    expect(screen.getByRole("button", { name: card.save })).toBeEnabled();
    await user.click(reportEmail);

    expect(screen.getByRole("button", { name: card.save })).toBeDisabled();
    expect(apiPatch).not.toHaveBeenCalled();
  });

  it("shows an error with Try again when the settings cannot be loaded", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respondWithRoutes(apiGet, {
      [PREFERENCES_PATH]: (): ApiResult => {
        return isFailing
          ? createErrorResult(500, "CONFLICT")
          : createSuccessResult(buildDefaultNotificationPreferences());
      },
    });
    renderSignedIn(<NotificationPreferencesCard />);

    expect(await screen.findByText(card.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: card.retry }));

    expect(
      await screen.findByRole("checkbox", { name: emailName(kinds.gapAssigned.title) }),
    ).toBeChecked();
  });
});
