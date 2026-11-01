import { describe, expect, it } from "vitest";
import { buildStoryGapsHref } from "./gap-path.util";

describe("buildStoryGapsHref", () => {
  it("links to the gaps tab of the story", () => {
    expect(buildStoryGapsHref("APP", "APP-1")).toBe("/projects/APP/stories/APP-1?tab=gaps");
  });

  it("encodes both keys", () => {
    expect(buildStoryGapsHref("A P", "A/1")).toBe("/projects/A%20P/stories/A%2F1?tab=gaps");
  });
});
