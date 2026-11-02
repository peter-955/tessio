import { describe, expect, it } from "vitest";
import { ASSIGNEE_ID, CURRENT_USER_ID } from "../test/utils/failure-fixture.util";
import type { FailureTimelineLabels } from "../typing/types/failure-timeline-labels.type";
import type { FailureEvent } from "../typing/types/failure.type";
import { buildFailureTimelineItems } from "./failure-event.util";

const LABELS: FailureTimelineLabels = {
  opened: "Failure opened",
  failedAgain: "Failed again",
  unassigned: "Unassigned",
  automatic: "Automatic",
  formatStatusChange: (fromStatus, toStatus) => {
    return `${fromStatus ?? "-"} → ${toStatus ?? "-"}`;
  },
  formatAssigned: (name) => {
    return `Assigned to ${name}`;
  },
  formatCauseChange: (fromCause, toCause) => {
    return `cause ${fromCause ?? "none"} to ${toCause ?? "none"}`;
  },
  formatActor: (name) => {
    return `by ${name}`;
  },
  formatTime: (isoDate) => {
    return `at ${isoDate}`;
  },
};

const buildEvent = (overrides: Partial<FailureEvent>): FailureEvent => {
  return {
    id: "e2000000-0000-4000-8000-000000000001",
    kind: "opened",
    fromStatus: null,
    toStatus: null,
    fromCause: null,
    toCause: null,
    caseResultId: null,
    runId: null,
    assigneeId: null,
    assigneeName: null,
    actorId: CURRENT_USER_ID,
    actorName: "Quinn Qc",
    createdAt: "2026-10-20T09:00:00Z",
    ...overrides,
  };
};

describe("buildFailureTimelineItems", () => {
  it("titles every event kind and picks its icon and colour", () => {
    const items = buildFailureTimelineItems(
      [
        buildEvent({ id: "1", kind: "opened", actorId: null, actorName: null }),
        buildEvent({ id: "2", kind: "failed_again", actorId: null, actorName: null }),
        buildEvent({ id: "3", kind: "status_changed", fromStatus: "open", toStatus: "fixed" }),
        buildEvent({ id: "4", kind: "status_changed", fromStatus: "fixed", toStatus: "verified" }),
        buildEvent({ id: "5", kind: "status_changed", fromStatus: "fixed", toStatus: "reopened" }),
        buildEvent({ id: "6", kind: "assigned", assigneeId: ASSIGNEE_ID, assigneeName: "Dana" }),
        buildEvent({ id: "7", kind: "unassigned" }),
      ],
      LABELS,
    );

    expect(
      items.map(({ key, title, icon, color }) => {
        return { key, title, icon, color };
      }),
    ).toEqual([
      { key: "1", title: "Failure opened", icon: "failures", color: "red" },
      { key: "2", title: "Failed again", icon: "failures", color: "red" },
      { key: "3", title: "open → fixed", icon: "check", color: "yellow" },
      { key: "4", title: "fixed → verified", icon: "circleCheck", color: "green" },
      { key: "5", title: "fixed → reopened", icon: "refresh", color: "red" },
      { key: "6", title: "Assigned to Dana", icon: "user", color: "tessio" },
      { key: "7", title: "Unassigned", icon: "user", color: "gray" },
    ]);
  });

  it("names the actor, or says the change was automatic", () => {
    const [automaticItem, manualItem] = buildFailureTimelineItems(
      [
        buildEvent({ id: "1", kind: "failed_again", actorId: null, actorName: null }),
        buildEvent({ id: "2", kind: "status_changed", fromStatus: "open", toStatus: "fixed" }),
      ],
      LABELS,
    );

    expect(automaticItem).toMatchObject({
      description: "Automatic",
      time: "at 2026-10-20T09:00:00Z",
    });
    expect(manualItem).toMatchObject({ description: "by Quinn Qc" });
  });
});
