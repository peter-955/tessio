import {
  ENVIRONMENT_URL_PATTERN,
  MAX_ENVIRONMENT_URL_LENGTH,
} from "../typing/constants/environment.constant";
import type { EnvironmentUrlError } from "../typing/types/environment-url-error.type";

export const findEnvironmentUrlError = (value: string): EnvironmentUrlError | null => {
  const url = value.trim();

  if (url.length > MAX_ENVIRONMENT_URL_LENGTH) {
    return "tooLong";
  }

  return ENVIRONMENT_URL_PATTERN.test(url) ? null : "invalid";
};
