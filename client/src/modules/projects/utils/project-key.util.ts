import {
  PROJECT_KEY_MAX_LENGTH,
  PROJECT_KEY_MIN_LENGTH,
  PROJECT_KEY_PATTERN,
} from "../typing/constants/project-key.constant";

export const normalizeProjectKeyInput = (value: string): string => {
  return value.toUpperCase().replace(/[^A-Z0-9]/g, "");
};

export const checkIsValidProjectKey = (value: string): boolean => {
  return PROJECT_KEY_PATTERN.test(value);
};

export const suggestProjectKey = (jiraProjectKey: string, name: string): string => {
  if (checkIsValidProjectKey(jiraProjectKey)) {
    return jiraProjectKey;
  }

  const suggestedKey = normalizeProjectKeyInput(name)
    .replace(/^[0-9]+/, "")
    .slice(0, PROJECT_KEY_MAX_LENGTH);

  return suggestedKey.length < PROJECT_KEY_MIN_LENGTH ? "" : suggestedKey;
};
