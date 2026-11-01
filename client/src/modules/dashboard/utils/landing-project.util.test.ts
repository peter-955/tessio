import { describe, expect, it } from "vitest";
import { selectLandingProjectKey } from "./landing-project.util";

const PROJECTS = [{ key: "BILL" }, { key: "SHOP" }];

describe("selectLandingProjectKey", () => {
  it("keeps the last opened project when it is still visible", () => {
    expect(selectLandingProjectKey(PROJECTS, "SHOP")).toBe("SHOP");
  });

  it("falls back to the first project when the last key is stale or missing", () => {
    expect(selectLandingProjectKey(PROJECTS, "GONE")).toBe("BILL");
    expect(selectLandingProjectKey(PROJECTS, null)).toBe("BILL");
  });

  it("returns null when there are no projects", () => {
    expect(selectLandingProjectKey([], "SHOP")).toBeNull();
    expect(selectLandingProjectKey([], null)).toBeNull();
  });
});
