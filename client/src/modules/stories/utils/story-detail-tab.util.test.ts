import { describe, expect, it } from "vitest";
import { StoryDetailTab } from "../typing/enums/story-detail-tab.enum";
import { parseStoryDetailTab } from "./story-detail-tab.util";

describe("parseStoryDetailTab", () => {
  const slots = { [StoryDetailTab.GAPS]: "gaps panel" };

  it("keeps overview and tabs that have a slot", () => {
    expect(parseStoryDetailTab("overview", {})).toBe(StoryDetailTab.OVERVIEW);
    expect(parseStoryDetailTab("gaps", slots)).toBe(StoryDetailTab.GAPS);
    expect(parseStoryDetailTab(["gaps", "runs"], slots)).toBe(StoryDetailTab.GAPS);
  });

  it("falls back to overview for unknown or unmounted tabs", () => {
    expect(parseStoryDetailTab(undefined, slots)).toBe(StoryDetailTab.OVERVIEW);
    expect(parseStoryDetailTab("history", slots)).toBe(StoryDetailTab.OVERVIEW);
    expect(parseStoryDetailTab("runs", slots)).toBe(StoryDetailTab.OVERVIEW);
  });
});
