import type { RunCase, RunCounts } from "@/shared/typing/types/test-run.type";
import { NO_STORY_GROUP_KEY } from "../typing/constants/suite.constant";
import type { RunStoryGroup } from "../typing/types/run-story-group.type";

export const groupRunCasesByStory = (cases: readonly RunCase[]): RunStoryGroup[] => {
  const groups = new Map<string, RunStoryGroup>();

  for (const runCase of cases) {
    const key = runCase.storyId ?? NO_STORY_GROUP_KEY;
    const group = groups.get(key);
    if (group === undefined) {
      groups.set(key, {
        key,
        storyJiraKey: runCase.storyJiraKey ?? null,
        storyTitle: runCase.storyTitle ?? null,
        cases: [runCase],
      });
      continue;
    }

    group.cases.push(runCase);
  }

  return [...groups.values()];
};

export const countRunCases = (cases: readonly RunCase[]): RunCounts => {
  const counts: RunCounts = {
    total: cases.length,
    passed: 0,
    failed: 0,
    blocked: 0,
    skipped: 0,
    notReported: 0,
  };

  for (const runCase of cases) {
    const status = runCase.result?.status;
    if (status === undefined) {
      counts.notReported += 1;
      continue;
    }

    counts[status] += 1;
  }

  return counts;
};
