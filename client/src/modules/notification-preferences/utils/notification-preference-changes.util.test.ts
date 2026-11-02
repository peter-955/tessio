import { describe, expect, it } from "vitest";
import { buildDefaultNotificationPreferences } from "../test/utils/notification-preference-fixture.util";
import {
  buildNotificationPreferenceChanges,
  setNotificationPreference,
} from "./notification-preference-changes.util";

describe("notification preference changes", () => {
  it("sets one channel of one kind and leaves the rest", () => {
    const saved = buildDefaultNotificationPreferences();

    const draft = setNotificationPreference(saved, "run_finished", "email", true);

    expect(draft.find((preference) => preference.kind === "run_finished")).toEqual({
      kind: "run_finished",
      inApp: true,
      email: true,
    });
    expect(draft.filter((preference) => preference.kind !== "run_finished")).toEqual(
      saved.filter((preference) => preference.kind !== "run_finished"),
    );
    expect(saved.find((preference) => preference.kind === "run_finished")?.email).toBe(false);
  });

  it("sends only the kinds and fields that changed", () => {
    const saved = buildDefaultNotificationPreferences();
    const withRunEmail = setNotificationPreference(saved, "run_finished", "email", true);
    const draft = setNotificationPreference(withRunEmail, "gap_assigned", "inApp", false);

    expect(buildNotificationPreferenceChanges(saved, draft)).toEqual([
      { kind: "gap_assigned", inApp: false },
      { kind: "run_finished", email: true },
    ]);
  });

  it("sends nothing when a change is undone", () => {
    const saved = buildDefaultNotificationPreferences();
    const changed = setNotificationPreference(saved, "report_ready", "email", true);
    const undone = setNotificationPreference(changed, "report_ready", "email", false);

    expect(buildNotificationPreferenceChanges(saved, undone)).toEqual([]);
  });
});
