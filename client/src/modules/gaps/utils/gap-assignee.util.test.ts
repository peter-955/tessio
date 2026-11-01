import { describe, expect, it } from "vitest";
import { createGap } from "../test/utils/gap.fixture";
import { describeAssignee } from "./gap-assignee.util";

describe("describeAssignee", () => {
  it("describes an active and a deactivated user", () => {
    expect(describeAssignee(createGap())).toEqual({
      kind: "user",
      name: "Bao Ba",
      isDeactivated: false,
    });
    expect(describeAssignee(createGap({ assigneeStatus: "deactivated" }))).toEqual({
      kind: "user",
      name: "Bao Ba",
      isDeactivated: true,
    });
  });

  it("describes a role-only assignment", () => {
    const gap = createGap({
      assigneeId: null,
      assigneeName: null,
      assigneeStatus: null,
      assigneeRole: "ba",
    });

    expect(describeAssignee(gap)).toEqual({ kind: "role", role: "ba" });
  });

  it("falls back to unassigned", () => {
    const unassignedGap = createGap({ assigneeId: null, assigneeName: null, assigneeStatus: null });
    const viewerRoleGap = createGap({
      assigneeId: null,
      assigneeName: null,
      assigneeStatus: null,
      assigneeRole: "viewer",
    });

    expect(describeAssignee(unassignedGap)).toEqual({ kind: "unassigned" });
    expect(describeAssignee(viewerRoleGap)).toEqual({ kind: "unassigned" });
  });
});
