"use client";

import { DSAlert, DSButton, DSDropzone, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./import-file-step.module.scss";

interface Props {
  onFileSelected: (file: File) => void;
  errorMessage: string | null;
  uploadPercent: number | null;
  isUploading: boolean;
  isReading: boolean;
  onCancelUpload: () => void;
}

export const ImportFileStep: FC<Props> = ({
  onFileSelected,
  errorMessage,
  uploadPercent,
  isUploading,
  isReading,
  onCancelUpload,
}) => {
  const { t } = useTranslation("testCases");

  const handleDrop = (files: File[]): void => {
    const [file] = files;
    if (file !== undefined) {
      onFileSelected(file);
    }
  };

  return (
    <DSStack gap={4}>
      <DSText color="muted">{t("import.fileHelp")}</DSText>
      <DSDropzone
        title={t("import.dropTitle")}
        description={t("import.dropDescription")}
        onDrop={handleDrop}
        isMultiple={false}
        isLoading={isUploading || isReading}
      />
      {isUploading && (
        <div className={styles.progress} role="status">
          <DSText size="sm">{t("import.uploading", { percent: uploadPercent ?? 0 })}</DSText>
          <DSButton type="ghost" size="sm" onClick={onCancelUpload}>
            {t("actions.cancelUpload")}
          </DSButton>
        </div>
      )}
      {isReading && (
        <div role="status">
          <DSText size="sm">{t("import.reading")}</DSText>
        </div>
      )}
      {errorMessage !== null && <DSAlert color="danger">{errorMessage}</DSAlert>}
    </DSStack>
  );
};
