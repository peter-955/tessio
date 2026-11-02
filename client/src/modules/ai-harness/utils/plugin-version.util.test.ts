import { describe, expect, it } from "vitest";
import {
  checkIsVersionAtLeast,
  parsePluginVersion,
  resolvePluginState,
} from "./plugin-version.util";

describe("parsePluginVersion", () => {
  it("reads MAJOR.MINOR.PATCH and refuses anything else", () => {
    expect(parsePluginVersion("0.3.0")).toEqual([0, 3, 0]);
    expect(parsePluginVersion(" 1.10.2 ")).toEqual([1, 10, 2]);
    expect(parsePluginVersion("v1.2.3")).toBeNull();
    expect(parsePluginVersion("1.2")).toBeNull();
  });
});

describe("checkIsVersionAtLeast", () => {
  it.each([
    ["0.3.0", "0.3.0", true],
    ["0.10.0", "0.9.0", true],
    ["1.0.0", "0.9.9", true],
    ["0.2.9", "0.3.0", false],
    ["v2", "0.3.0", false],
  ])("compares %s with %s by number", (sent, required, expected) => {
    expect(checkIsVersionAtLeast(sent, required)).toBe(expected);
  });
});

describe("resolvePluginState", () => {
  it("is unused without a version, current when new enough and outdated otherwise", () => {
    expect(resolvePluginState(null, "0.3.0")).toBe("unused");
    expect(resolvePluginState("0.3.0", "0.3.0")).toBe("current");
    expect(resolvePluginState("0.2.0", "0.3.0")).toBe("outdated");
  });
});
