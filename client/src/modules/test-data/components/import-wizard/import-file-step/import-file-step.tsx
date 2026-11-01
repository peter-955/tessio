"use client";

import {
  DSAlert,
  DSButton,
  DSDropzone,
  DSSelect,
  DSStack,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./import-file-step.module.scss";

interface Props {
  scopeId: string;
  scopeOptions: DSSelectOption<string>[];
  onScopeChange: (scopeId: string) => void;
  onFileSelected: (file: File) => void;
  errorMessage: string | null;
  uploadPercent: number | null;
  isUploading: boolean;
  isReading: boolean;
  onCancelUpload: () => void;
}

export const ImportFileStep: FC<Props> = ({
  scopeId,
  scopeOptions,
  onScopeChange,
  onFileSelected,
  errorMessage,
  uploadPercent,
  isUploading,
  isReading,
  onCancelUpload,
}) => {
  const { t } = useTranslation("testData");
  const isBusy = isUploading || isReading;

  const handleDrop = (files: File[]): void => {
    const [file] = files;
    if (file !== undefined) {
      onFileSelected(file);
    }
  };

  const handleScopeChange = (value: string | null): void => {
    if (value !== null) {
      onScopeChange(value);
    }
  };

  return (
    <DSStack gap={4}>
      <DSText color="muted">{t("import.fileStepTitle")}</DSText>
      <DSSelect
        label={t("import.scope")}
        value={scopeId}
        options={scopeOptions}
        onChange={handleScopeChange}
        isDisabled={isBusy}
        isRequired
      />
      <DSDropzone
        title={t("import.dropTitle")}
        description={t("import.dropDescription")}
        onDrop={handleDrop}
        isMultiple={false}
        isLoading={isBusy}
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
