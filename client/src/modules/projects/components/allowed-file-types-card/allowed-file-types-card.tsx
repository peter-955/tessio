"use client";

import {
  DSButton,
  DSCard,
  DSInput,
  DSMultiSelect,
  DSStack,
  useDSForm,
} from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchProject } from "../../hooks/mutations/use-patch-project";
import {
  DEFAULT_ALLOWED_FILE_TYPES,
  MAX_ALLOWED_FILE_TYPES,
} from "../../typing/constants/file-type.constant";
import type { AllowedFileTypesValues } from "../../typing/types/allowed-file-types-values.type";
import { buildFileTypeOptions, checkIsValidMimeType } from "../../utils/file-type.util";
import { buildAllowedFileTypesValues } from "../../utils/project-settings.util";
import { SettingsCardFooter } from "../settings-card-footer/settings-card-footer";
import styles from "./allowed-file-types-card.module.scss";

interface Props {
  project: Project;
}

export const AllowedFileTypesCard: FC<Props> = ({ project }) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast } = useShowToast();
  const { mutate: patchProject, isPending: isSaving } = usePatchProject(project.key);
  const [otherType, setOtherType] = useState("");
  const [otherTypeError, setOtherTypeError] = useState<string | undefined>(undefined);
  const form = useDSForm<AllowedFileTypesValues>({
    mode: "controlled",
    initialValues: buildAllowedFileTypesValues(project),
    validate: {
      allowedFileTypes: (value) => {
        if (value.length === 0) {
          return t("settings.fileTypes.atLeastOne");
        }

        return value.length > MAX_ALLOWED_FILE_TYPES ? t("settings.fileTypes.tooMany") : null;
      },
    },
  });
  const { allowedFileTypes } = form.values;

  const handleFileTypesChange = (fileTypes: string[]): void => {
    form.setFieldValue("allowedFileTypes", fileTypes);
  };

  const handleOtherTypeChange = (value: string): void => {
    setOtherType(value);
    setOtherTypeError(undefined);
  };

  const handleAddOtherType = (): void => {
    const mimeType = otherType.trim().toLowerCase();
    if (!checkIsValidMimeType(mimeType)) {
      setOtherTypeError(t("settings.fileTypes.invalidType"));
      return;
    }

    if (!allowedFileTypes.includes(mimeType)) {
      if (allowedFileTypes.length >= MAX_ALLOWED_FILE_TYPES) {
        setOtherTypeError(t("settings.fileTypes.tooMany"));
        return;
      }

      handleFileTypesChange([...allowedFileTypes, mimeType]);
    }
    setOtherType("");
  };

  const handleReset = (): void => {
    handleFileTypesChange([...DEFAULT_ALLOWED_FILE_TYPES]);
  };

  const handleValidSubmit = (values: AllowedFileTypesValues): void => {
    patchProject(
      { allowedFileTypes: values.allowedFileTypes },
      {
        onSuccess: (updatedProject) => {
          const savedValues = buildAllowedFileTypesValues(updatedProject);
          showSuccessToast(t("settings.saved"));
          form.setInitialValues(savedValues);
          form.setValues(savedValues);
          form.resetDirty(savedValues);
        },
      },
    );
  };

  return (
    <DSCard title={t("settings.fileTypes.title")}>
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSMultiSelect
            label={t("settings.fileTypes.label")}
            value={allowedFileTypes}
            options={buildFileTypeOptions(allowedFileTypes)}
            onChange={handleFileTypesChange}
            description={t("settings.fileTypes.description")}
            error={form.errors.allowedFileTypes}
            maxValues={MAX_ALLOWED_FILE_TYPES}
            nothingFoundLabel={t("hints.noMatch")}
            isRequired
          />
          <div className={styles.otherType}>
            <div className={styles.otherTypeInput}>
              <DSInput
                label={t("settings.fileTypes.otherType")}
                value={otherType}
                onChange={handleOtherTypeChange}
                placeholder="text/markdown"
                error={otherTypeError}
                autoComplete="off"
              />
            </div>
            <DSButton icon="plus" isDisabled={otherType.trim() === ""} onClick={handleAddOtherType}>
              {t("settings.fileTypes.add")}
            </DSButton>
          </div>
          <SettingsCardFooter isDirty={form.isDirty()} isSaving={isSaving}>
            <DSButton type="ghost" icon="refresh" onClick={handleReset}>
              {t("settings.fileTypes.reset")}
            </DSButton>
          </SettingsCardFooter>
        </DSStack>
      </form>
    </DSCard>
  );
};
