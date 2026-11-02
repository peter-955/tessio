import type { JunitFileError } from "../types/junit-file-error.type";

export const MAX_JUNIT_FILE_BYTES = 10 * 1024 * 1024;

export const JUNIT_FILE_EXTENSION = ".xml";

export const JUNIT_FORM_FIELDS = {
  file: "file",
  environment: "environment",
  suite: "suite",
} as const;

export const JUNIT_FILE_ERROR_KEYS = {
  notXml: "errors.notXml",
  tooLarge: "errors.tooLarge",
  empty: "errors.empty",
} as const satisfies Record<JunitFileError, string>;

export const JUNIT_IMPORT_SKELETON_LINE_COUNT = 3;
