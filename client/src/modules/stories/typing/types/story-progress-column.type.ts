export type StoryProgressColumnLabel = "coverage" | "openGaps" | "failures" | "lastRun";

export interface StoryProgressColumn {
  label: StoryProgressColumnLabel;
  isNumeric: boolean;
}
