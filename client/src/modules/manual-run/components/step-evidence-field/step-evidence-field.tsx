"use client";

import { DSAlert, DSButton, DSDropzone, DSIcon, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useSignedUpload } from "@/lib/uploads/hooks/use-signed-upload";
import { UploadCanceledError } from "@/lib/uploads/upload-canceled-error";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useFormatMegabytes } from "../../hooks/use-format-megabytes";
import { useManualRunApiErrors } from "../../hooks/use-manual-run-api-errors";
import type { StepDraft } from "../../typing/types/step-draft.type";
import styles from "./step-evidence-field.module.scss";

interface Props {
  stepDraft: StepDraft;
  onChange: (changes: Partial<StepDraft>) => void;
}

export const StepEvidenceField: FC<Props> = ({ stepDraft, onChange }) => {
  const { t } = useTranslation("manualRun");
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useManualRunApiErrors();
  const formatMegabytes = useFormatMegabytes();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDropzoneShown, setIsDropzoneShown] = useState(false);
  const signedUpload = useSignedUpload({
    target: {
      kind: "evidence",
      projectKey: project.key,
      allowedFileTypes: project.allowedFileTypes,
    },
    apiErrors,
    isGlobalErrorToastDisabled: true,
  });

  const handleDrop = async (files: File[]): Promise<void> => {
    const [file] = files;
    if (file === undefined) {
      return;
    }

    setErrorMessage(null);
    onChange({ isUploading: true });

    try {
      const uploadedFile = await signedUpload.upload(file);
      onChange({ evidenceFile: uploadedFile, isUploading: false });
    } catch (error) {
      onChange({ isUploading: false });
      if (!(error instanceof UploadCanceledError)) {
        setErrorMessage(resolveMessage(error, apiErrors));
      }
    }
  };

  const handleRemove = (): void => {
    signedUpload.reset();
    onChange({ evidenceFile: null });
  };

  const renderContent = (): ReactNode => {
    if (stepDraft.isUploading) {
      return (
        <div className={styles.row} role="status">
          <DSText size="sm" component="span">
            {t("evidence.uploading", { percent: signedUpload.progress?.percent ?? 0 })}
          </DSText>
          <DSButton type="ghost" size="sm" onClick={signedUpload.cancel}>
            {t("evidence.cancel")}
          </DSButton>
        </div>
      );
    }

    if (stepDraft.evidenceFile !== null) {
      return (
        <div className={styles.row}>
          <span className={styles.file}>
            <DSIcon name="file" size={16} />
            <DSText size="sm" component="span" className={styles.fileName}>
              {stepDraft.evidenceFile.fileName}
            </DSText>
          </span>
          <DSButton type="ghost" size="sm" icon="trash" onClick={handleRemove}>
            {t("evidence.remove")}
          </DSButton>
        </div>
      );
    }

    return (
      <DSDropzone
        title={t("evidence.drop")}
        description={t("evidence.dropDescription", {
          size: formatMegabytes(signedUpload.rules.maxSizeInBytes),
        })}
        onDrop={(files) => {
          void handleDrop(files);
        }}
        acceptedTypes={signedUpload.rules.acceptedTypes}
        isMultiple={false}
      />
    );
  };

  if (!isDropzoneShown && !stepDraft.isUploading && stepDraft.evidenceFile === null) {
    return (
      <div className={styles.attach}>
        <DSButton
          type="ghost"
          size="sm"
          icon="upload"
          onClick={() => {
            setIsDropzoneShown(true);
          }}
        >
          {t("evidence.attach")}
        </DSButton>
      </div>
    );
  }

  return (
    <div className={styles.field}>
      <DSText size="sm" weight="medium" component="span">
        {t("evidence.label")}
      </DSText>
      {renderContent()}
      {errorMessage !== null && <DSAlert color="danger">{errorMessage}</DSAlert>}
    </div>
  );
};
