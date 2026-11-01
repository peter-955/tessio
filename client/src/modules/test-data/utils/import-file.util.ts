import {
  DOTENV_FILE_NAME_PREFIX,
  IMPORT_FILE_EXTENSIONS,
  JSON_CONTENT_TYPE,
  JSON_FILE_EXTENSION,
  MAX_IMPORT_SIZE_IN_BYTES,
  TEXT_CONTENT_TYPE,
} from "../typing/constants/test-data.constant";
import type { ImportFileError } from "../typing/types/import-file-error.type";

const hasImportFileName = (fileName: string): boolean => {
  const normalizedName = fileName.toLowerCase();

  return (
    normalizedName.startsWith(DOTENV_FILE_NAME_PREFIX) ||
    IMPORT_FILE_EXTENSIONS.some((extension) => normalizedName.endsWith(extension))
  );
};

export const findImportFileError = (file: File): ImportFileError | null => {
  if (!hasImportFileName(file.name)) {
    return "extension";
  }

  return file.size > MAX_IMPORT_SIZE_IN_BYTES ? "size" : null;
};

export const prepareImportFile = (file: File): File => {
  const isJson = file.name.toLowerCase().endsWith(JSON_FILE_EXTENSION);

  return new File([file], file.name, { type: isJson ? JSON_CONTENT_TYPE : TEXT_CONTENT_TYPE });
};
