import { describe, expect, it } from "vitest";
import { buildSprintPath, buildSprintsPath } from "./sprint-path.util";

describe("sprint paths", () => {
  it("builds the list and detail paths", () => {
    expect(buildSprintsPath("SHOP")).toBe("/projects/SHOP/sprints");
    expect(buildSprintPath("SHOP", "5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70")).toBe(
      "/projects/SHOP/sprints/5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70",
    );
  });
});
