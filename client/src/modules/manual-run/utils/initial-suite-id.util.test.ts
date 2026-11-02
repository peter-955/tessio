import { describe, expect, it } from "vitest";
import { parseInitialSuiteId } from "./initial-suite-id.util";

describe("parseInitialSuiteId", () => {
  it("keeps a suite id in lower case", () => {
    expect(parseInitialSuiteId(" 5A000000-0000-4000-8000-000000000001 ")).toBe(
      "5a000000-0000-4000-8000-000000000001",
    );
    expect(parseInitialSuiteId(["5a000000-0000-4000-8000-000000000002", "x"])).toBe(
      "5a000000-0000-4000-8000-000000000002",
    );
  });

  it("ignores a missing or invalid suite id", () => {
    expect(parseInitialSuiteId(undefined)).toBeNull();
    expect(parseInitialSuiteId("smoke")).toBeNull();
  });
});
