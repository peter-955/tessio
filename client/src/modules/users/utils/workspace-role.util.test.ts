import { describe, expect, it } from "vitest";
import { findAssignableWorkspaceRole } from "./workspace-role.util";

describe("findAssignableWorkspaceRole", () => {
  it.each([
    ["admin", "admin"],
    ["member", "member"],
    ["owner", null],
  ] as const)("maps %s to %s", (role, expected) => {
    expect(findAssignableWorkspaceRole(role)).toBe(expected);
  });
});
