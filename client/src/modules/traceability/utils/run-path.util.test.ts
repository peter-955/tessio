import { describe, expect, it } from "vitest";
import { buildRunPath } from "./run-path.util";

describe("buildRunPath", () => {
  it("builds the project run path", () => {
    expect(buildRunPath("SHOP", "f1000000-0000-4000-8000-000000000001")).toBe(
      "/projects/SHOP/runs/f1000000-0000-4000-8000-000000000001",
    );
  });
});
