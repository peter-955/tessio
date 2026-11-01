import type { DSSelectOption } from "@/components/design-system";
import {
  KNOWN_FILE_TYPES,
  MIME_TYPE_MAX_LENGTH,
  MIME_TYPE_PATTERN,
} from "../typing/constants/file-type.constant";

export const checkIsValidMimeType = (value: string): boolean => {
  return value.length <= MIME_TYPE_MAX_LENGTH && MIME_TYPE_PATTERN.test(value);
};

export const buildFileTypeOptions = (selectedMimeTypes: string[]): DSSelectOption<string>[] => {
  const knownOptions = KNOWN_FILE_TYPES.map((fileType): DSSelectOption<string> => {
    return { value: fileType.mimeType, label: `${fileType.formatLabel} (${fileType.mimeType})` };
  });
  const knownMimeTypes = new Set(KNOWN_FILE_TYPES.map((fileType) => fileType.mimeType));
  const customOptions = selectedMimeTypes
    .filter((mimeType) => {
      return !knownMimeTypes.has(mimeType);
    })
    .map((mimeType): DSSelectOption<string> => {
      return { value: mimeType, label: mimeType };
    });

  return [...knownOptions, ...customOptions];
};
