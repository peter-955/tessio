import type { RunCase } from "@/shared/typing/types/test-run.type";

export interface RunStoryGroup {
  key: string;
  storyJiraKey: string | null;
  storyTitle: string | null;
  cases: RunCase[];
}
