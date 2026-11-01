const TEXT_FILE_TYPE = "text/plain;charset=utf-8";

export const downloadTextFile = (fileName: string, content: string): void => {
  const blob = new Blob([content], { type: TEXT_FILE_TYPE });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = fileName;
  anchor.hidden = true;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
};
