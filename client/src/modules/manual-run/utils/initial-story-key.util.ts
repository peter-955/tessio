import { STORY_KEY_PATTERN } from "../typing/constants/manual-run.constant";

export const parseInitialStoryKey = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;
  const storyKey = firstValue?.trim().toUpperCase() ?? "";

  return STORY_KEY_PATTERN.test(storyKey) ? storyKey : null;
};
