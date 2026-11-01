export type CaseImportFileError = "extension" | "size";

export type CaseImportErrorKey =
  | CaseImportFileError
  | "invalidFile"
  | "uploadNotCompleted"
  | "notFound"
  | "choiceInvalid"
  | "typeNotAllowed";

export type CaseImportStage = "preview" | "commit";
