import {
  JUNIT_FILE_EXTENSION,
  MAX_JUNIT_FILE_BYTES,
} from "../typing/constants/junit-import.constant";
import type { JunitFileError } from "../typing/types/junit-file-error.type";

export const findJunitFileError = (file: Pick<File, "name" | "size">): JunitFileError | null => {
  if (!file.name.toLowerCase().endsWith(JUNIT_FILE_EXTENSION)) {
    return "notXml";
  }

  if (file.size === 0) {
    return "empty";
  }

  if (file.size > MAX_JUNIT_FILE_BYTES) {
    return "tooLarge";
  }

  return null;
};
