import { describe, expect, it } from "vitest";
import { parseVersionNumber } from "./version-parameter.util";

describe("parseVersionNumber", () => {
  it("reads a positive whole version number", () => {
    expect(parseVersionNumber("3")).toBe(3);
  });

  it("ignores a missing or invalid value", () => {
    expect(parseVersionNumber(null)).toBeNull();
    expect(parseVersionNumber("0")).toBeNull();
    expect(parseVersionNumber("2.5")).toBeNull();
    expect(parseVersionNumber("latest")).toBeNull();
  });
});
