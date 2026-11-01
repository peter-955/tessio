import { describe, expect, it } from "vitest";
import { parseInitialStoryKey } from "./initial-story-key.util";

describe("parseInitialStoryKey", () => {
  it("trims and uppercases the story key", () => {
    expect(parseInitialStoryKey("  shop-12 ")).toBe("SHOP-12");
  });

  it("takes the first value of a repeated parameter", () => {
    expect(parseInitialStoryKey(["shop-1", "shop-2"])).toBe("SHOP-1");
  });

  it("returns null for a missing, empty or malformed key", () => {
    expect(parseInitialStoryKey(undefined)).toBeNull();
    expect(parseInitialStoryKey("   ")).toBeNull();
    expect(parseInitialStoryKey("not a key")).toBeNull();
  });
});
