import type { TestStatus } from "./story.type";

export interface StoryFilters {
  sprintId: string | null;
  testStatus: TestStatus | null;
  query: string;
}

export interface StoryListQuery {
  sprintId?: string;
  testStatus?: TestStatus;
  query?: string;
}

export type StorySearchParams = Record<string, string | string[] | undefined>;
