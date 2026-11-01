import { describe, expect, it } from "vitest";
import { buildStoryProgress } from "../test/utils/story-progress-fixture.util";
import { mapStoryProgressById } from "./story-progress.util";

describe("mapStoryProgressById", () => {
  it("indexes the progress by story id", () => {
    const first = buildStoryProgress();
    const second = buildStoryProgress({
      storyId: "c1000000-0000-4000-8000-000000000002",
      jiraKey: "SHOP-2",
    });

    const progressById = mapStoryProgressById([first, second]);

    expect(progressById.size).toBe(2);
    expect(progressById.get(first.storyId)).toBe(first);
    expect(progressById.get(second.storyId)).toBe(second);
    expect(progressById.get("missing")).toBeUndefined();
  });
});
