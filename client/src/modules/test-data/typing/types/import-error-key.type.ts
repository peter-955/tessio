import type { ImportFileError } from "./import-file-error.type";

export type ImportErrorKey =
  ImportFileError | "typeNotAllowed" | "invalidFile" | "uploadNotCompleted";
