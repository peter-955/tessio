import {
  MAX_SUITE_DESCRIPTION_LENGTH,
  MAX_SUITE_NAME_LENGTH,
} from "../typing/constants/suite.constant";

export type SuiteNameError = "required" | "tooLong";

export const findSuiteNameError = (value: string): SuiteNameError | null => {
  const name = value.trim();
  if (name === "") {
    return "required";
  }

  return name.length > MAX_SUITE_NAME_LENGTH ? "tooLong" : null;
};

export const checkIsSuiteDescriptionTooLong = (value: string): boolean => {
  return value.trim().length > MAX_SUITE_DESCRIPTION_LENGTH;
};
