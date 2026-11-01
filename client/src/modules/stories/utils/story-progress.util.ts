import type { StoryProgress } from "@/modules/traceability/typing/types/traceability.type";

export const mapStoryProgressById = (
  progressList: readonly StoryProgress[],
): ReadonlyMap<string, StoryProgress> => {
  return new Map(
    progressList.map((progress) => {
      return [progress.storyId, progress];
    }),
  );
};
