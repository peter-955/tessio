export const buildFileReference = (fileKey: string): string => {
  return `{{file.${fileKey}}}`;
};
