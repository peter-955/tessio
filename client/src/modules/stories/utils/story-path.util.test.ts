import { describe, expect, it } from "vitest";
import { buildStoriesPath, buildStoryPath } from "./story-path.util";

describe("story paths", () => {
  it("builds the list and detail paths", () => {
    expect(buildStoriesPath("SHOP")).toBe("/projects/SHOP/stories");
    expect(buildStoryPath("SHOP", "SHOP-12")).toBe("/projects/SHOP/stories/SHOP-12");
  });
});
