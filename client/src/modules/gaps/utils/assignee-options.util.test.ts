import { describe, expect, it } from "vitest";
import { ASSIGNEE_ID, ROLE_LABELS, createGap, createMember } from "../test/utils/gap.fixture";
import type { AssigneeOptionLabels } from "../typing/types/assignee-option-labels.type";
import {
  buildAssigneeChoiceValue,
  buildAssigneeOptions,
  buildMemberOptions,
  buildReassignBody,
  parseAssigneeChoice,
} from "./assignee-options.util";

const LABELS: AssigneeOptionLabels = {
  formatRole: (role) => {
    return ROLE_LABELS[role];
  },
  formatAnyRole: (role) => {
    return `Any ${ROLE_LABELS[role]}`;
  },
};

const MEMBERS = [
  createMember(),
  createMember({
    userId: "a1000000-0000-4000-8000-000000000010",
    name: "Vi Viewer",
    role: "viewer",
  }),
  createMember({
    userId: "a1000000-0000-4000-8000-000000000011",
    name: "Dee Deactivated",
    role: "qc",
    userStatus: "deactivated",
  }),
  createMember({ userId: "a1000000-0000-4000-8000-000000000012", name: "Quinn Qc", role: "qc" }),
];

describe("assignee options", () => {
  it("lists active non-viewer members, then every assignable role", () => {
    expect(buildAssigneeOptions(MEMBERS, LABELS)).toEqual([
      { value: `member:${ASSIGNEE_ID}`, label: "Bao Ba · BA" },
      { value: "member:a1000000-0000-4000-8000-000000000012", label: "Quinn Qc · QC" },
      { value: "role:admin", label: "Any Admin" },
      { value: "role:pm", label: "Any PM" },
      { value: "role:ba", label: "Any BA" },
      { value: "role:qc", label: "Any QC" },
      { value: "role:dev", label: "Any Dev" },
    ]);
  });

  it("lists plain member ids for the raise form", () => {
    expect(buildMemberOptions(MEMBERS, LABELS.formatRole)).toEqual([
      { value: ASSIGNEE_ID, label: "Bao Ba · BA" },
      { value: "a1000000-0000-4000-8000-000000000012", label: "Quinn Qc · QC" },
    ]);
  });

  it("parses member and role choices and rejects anything else", () => {
    expect(parseAssigneeChoice(`member:${ASSIGNEE_ID}`)).toEqual({
      kind: "member",
      userId: ASSIGNEE_ID,
    });
    expect(parseAssigneeChoice("role:qc")).toEqual({ kind: "role", role: "qc" });
    expect(parseAssigneeChoice("role:viewer")).toBeNull();
    expect(parseAssigneeChoice("member:")).toBeNull();
    expect(parseAssigneeChoice("someone")).toBeNull();
    expect(parseAssigneeChoice(null)).toBeNull();
  });

  it("builds the current choice and the reassign body", () => {
    expect(buildAssigneeChoiceValue(createGap())).toBe(`member:${ASSIGNEE_ID}`);
    expect(
      buildAssigneeChoiceValue(
        createGap({ assigneeId: null, assigneeName: null, assigneeRole: "dev" }),
      ),
    ).toBe("role:dev");
    expect(
      buildAssigneeChoiceValue(createGap({ assigneeId: null, assigneeName: null })),
    ).toBeNull();
    expect(buildReassignBody({ kind: "member", userId: ASSIGNEE_ID })).toEqual({
      assigneeId: ASSIGNEE_ID,
    });
    expect(buildReassignBody({ kind: "role", role: "qc" })).toEqual({ assigneeRole: "qc" });
  });
});
