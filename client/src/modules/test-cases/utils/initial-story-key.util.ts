import { STORY_KEY_PATTERN } from "../typing/constants/test-case.constant";

export const parseInitialStoryKey = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue !== undefined && STORY_KEY_PATTERN.test(firstValue)
    ? firstValue.toUpperCase()
    : null;
};
