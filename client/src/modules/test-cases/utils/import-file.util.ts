import {
  CSV_CONTENT_TYPE,
  CSV_FILE_EXTENSION,
  MAX_CASE_IMPORT_SIZE_IN_BYTES,
  XLSX_CONTENT_TYPE,
  XLSX_FILE_EXTENSION,
} from "../typing/constants/test-case.constant";
import type { CaseImportFileError } from "../typing/types/case-import-error-key.type";

const checkIsXlsxFile = (file: File): boolean => {
  return file.name.toLowerCase().endsWith(XLSX_FILE_EXTENSION);
};

const checkIsCsvFile = (file: File): boolean => {
  return file.name.toLowerCase().endsWith(CSV_FILE_EXTENSION);
};

export const findCaseImportFileError = (file: File): CaseImportFileError | null => {
  if (!checkIsXlsxFile(file) && !checkIsCsvFile(file)) {
    return "extension";
  }

  return file.size > MAX_CASE_IMPORT_SIZE_IN_BYTES ? "size" : null;
};

export const prepareCaseImportFile = (file: File): File => {
  return new File([file], file.name, {
    type: checkIsXlsxFile(file) ? XLSX_CONTENT_TYPE : CSV_CONTENT_TYPE,
  });
};
