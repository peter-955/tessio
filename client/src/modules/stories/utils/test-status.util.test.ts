import { describe, expect, it } from "vitest";
import { checkIsSignOffStatus } from "./test-status.util";

describe("checkIsSignOffStatus", () => {
  it("is true only for passed and failed", () => {
    expect(checkIsSignOffStatus("passed")).toBe(true);
    expect(checkIsSignOffStatus("failed")).toBe(true);
    expect(checkIsSignOffStatus("ready_for_test")).toBe(false);
    expect(checkIsSignOffStatus("not_started")).toBe(false);
  });
});
