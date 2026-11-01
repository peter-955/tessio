import { describe, expect, it } from "vitest";
import { buildProjectPath, buildUserAccessPath } from "./user-path.util";

describe("user paths", () => {
  it("builds the access path of a user", () => {
    expect(buildUserAccessPath("abc")).toBe("/users/abc");
  });

  it("builds the path of a project", () => {
    expect(buildProjectPath("SHOP")).toBe("/projects/SHOP");
  });
});
