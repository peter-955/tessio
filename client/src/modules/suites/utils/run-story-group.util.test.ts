import { createRunCase } from "@/modules/runs/test/utils/run.fixture";
import { describe, expect, it } from "vitest";
import { countRunCases, groupRunCasesByStory } from "./run-story-group.util";

const PAY_STORY = {
  storyId: "c6000000-0000-4000-8000-000000000001",
  storyJiraKey: "APP-1",
  storyTitle: "Pay by card",
};

const REFUND_STORY = {
  storyId: "c6000000-0000-4000-8000-000000000002",
  storyJiraKey: "APP-2",
  storyTitle: "Refunds",
};

describe("groupRunCasesByStory", () => {
  it("groups the cases by story in the order of each story's first case", () => {
    const groups = groupRunCasesByStory([
      createRunCase({ code: "TC-1", ...PAY_STORY }),
      createRunCase({ code: "TC-2", ...REFUND_STORY }),
      createRunCase({ code: "TC-3", ...PAY_STORY }),
    ]);

    expect(
      groups.map((group) => {
        return [
          group.storyJiraKey,
          group.cases.map((runCase) => {
            return runCase.code;
          }),
        ];
      }),
    ).toEqual([
      ["APP-1", ["TC-1", "TC-3"]],
      ["APP-2", ["TC-2"]],
    ]);
  });

  it("puts cases without a story in one group", () => {
    const groups = groupRunCasesByStory([createRunCase({ code: "TC-1" })]);

    expect(groups).toHaveLength(1);
    expect(groups[0].storyJiraKey).toBeNull();
  });
});

describe("countRunCases", () => {
  it("counts each result and the cases not reported", () => {
    expect(
      countRunCases([
        createRunCase(),
        createRunCase({ result: null }),
        createRunCase({
          result: {
            id: "r2",
            status: "blocked",
            durationMs: null,
            suspectedCause: null,
            causeReason: null,
            recordedAt: "2026-10-20T10:00:00Z",
            iteration: 0,
          },
        }),
      ]),
    ).toEqual({ total: 3, passed: 1, failed: 0, blocked: 1, skipped: 0, notReported: 1 });
  });
});
