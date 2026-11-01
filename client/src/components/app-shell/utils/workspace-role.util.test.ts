import { describe, expect, it } from "vitest";
import { checkIsWorkspaceAdmin } from "./workspace-role.util";

describe("checkIsWorkspaceAdmin", () => {
  it("is true for owners and admins only", () => {
    expect(checkIsWorkspaceAdmin("owner")).toBe(true);
    expect(checkIsWorkspaceAdmin("admin")).toBe(true);
    expect(checkIsWorkspaceAdmin("member")).toBe(false);
  });
});
