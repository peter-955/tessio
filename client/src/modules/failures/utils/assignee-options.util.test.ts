import type { ProjectRole } from "@/components/project-context/typing/types/project.type";
import { describe, expect, it } from "vitest";
import {
  ASSIGNEE_ID,
  CURRENT_USER_ID,
  DEACTIVATED_USER_ID,
  INVITED_USER_ID,
  MEMBERS,
} from "../test/utils/failure-fixture.util";
import { buildAssigneeFilterOptions, buildAssignOptions } from "./assignee-options.util";

const ROLE_LABELS: Record<ProjectRole, string> = {
  admin: "Admin",
  pm: "PM",
  ba: "BA",
  qc: "QC",
  dev: "Dev",
  viewer: "Viewer",
};

describe("assignee options", () => {
  it("offers Unassigned then the active members sorted by name", () => {
    expect(
      buildAssignOptions(MEMBERS, {
        unassigned: "Unassigned",
        formatRole: (role) => {
          return ROLE_LABELS[role];
        },
      }),
    ).toEqual([
      { value: "__unassigned__", label: "Unassigned" },
      { value: ASSIGNEE_ID, label: "Dev Dana · Dev" },
      { value: CURRENT_USER_ID, label: "Quinn Qc · QC" },
    ]);
  });

  it("filters by anyone, unassigned, me or any member, deactivated included", () => {
    expect(
      buildAssigneeFilterOptions(MEMBERS, {
        anyone: "Anyone",
        unassigned: "Unassigned",
        me: "Assigned to me",
        formatDeactivated: (name) => {
          return `${name} (Deactivated)`;
        },
      }),
    ).toEqual([
      { value: "__any__", label: "Anyone" },
      { value: "unassigned", label: "Unassigned" },
      { value: "me", label: "Assigned to me" },
      { value: DEACTIVATED_USER_ID, label: "Ann Old (Deactivated)" },
      { value: ASSIGNEE_ID, label: "Dev Dana" },
      { value: INVITED_USER_ID, label: "Ivy New" },
      { value: CURRENT_USER_ID, label: "Quinn Qc" },
    ]);
  });
});
