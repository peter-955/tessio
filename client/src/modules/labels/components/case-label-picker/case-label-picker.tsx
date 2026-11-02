"use client";

import {
  DSAlert,
  DSButton,
  DSGroup,
  DSInput,
  DSMultiSelect,
  DSStack,
  DSText,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostLabel } from "../../hooks/mutations/use-post-label";
import { usePutTestCaseLabels } from "../../hooks/mutations/use-put-test-case-labels";
import { useGetLabels } from "../../hooks/queries/use-get-labels";
import { useLabelNameErrorText } from "../../hooks/use-label-name-error-text";
import { DEFAULT_LABEL_COLOR, MAX_LABELS_PER_CASE } from "../../typing/constants/label.constant";
import type { CaseLabel } from "../../typing/types/label.type";
import { findLabelByName, findLabelNameError } from "../../utils/label-name.util";
import { buildLabelOptions, checkHasSameLabelIds } from "../../utils/label-options.util";
import { LabelChips } from "../label-chips/label-chips";
import styles from "./case-label-picker.module.scss";

interface Props {
  projectKey: string;
  caseCode: string;
  labels: readonly CaseLabel[];
  canEdit: boolean;
}

export const CaseLabelPicker: FC<Props> = ({ projectKey, caseCode, labels, canEdit }) => {
  const { t } = useTranslation("labels");
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const toNameErrorText = useLabelNameErrorText();
  const [isEditing, setIsEditing] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [newName, setNewName] = useState("");
  const [newNameError, setNewNameError] = useState<string | null>(null);
  const projectLabels = useGetLabels(projectKey, isEditing);
  const availableLabels = projectLabels.data ?? [];
  const isAtMax = selectedIds.length >= MAX_LABELS_PER_CASE;
  const saveLabels = usePutTestCaseLabels(projectKey, caseCode, {
    onSuccess: () => {
      showSuccessToast(t("toasts.caseLabelsSaved"));
      setIsEditing(false);
    },
  });
  const createLabel = usePostLabel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: (label) => {
      setSelectedIds((currentIds) => [...currentIds, label.id]);
      setNewName("");
    },
    onError: (error: ApiError) => {
      if (error.code === "CONFLICT") {
        setNewNameError(t("errors.nameAlreadyUsed"));
        void projectLabels.refetch();
        return;
      }

      showErrorToast(resolveMessage(error));
    },
  });

  const startEditing = (): void => {
    setSelectedIds(labels.map((label) => label.id));
    setNewName("");
    setNewNameError(null);
    setIsEditing(true);
  };

  const handleNewNameChange = (value: string): void => {
    setNewName(value);
    setNewNameError(null);
  };

  const handleCreate = (): void => {
    const nameError = findLabelNameError(newName, availableLabels);
    const existingLabel = findLabelByName(availableLabels, newName);
    if (nameError === "alreadyUsed" && existingLabel !== undefined) {
      if (!selectedIds.includes(existingLabel.id)) {
        if (isAtMax) {
          setNewNameError(t("picker.maxReached", { max: MAX_LABELS_PER_CASE }));
          return;
        }

        setSelectedIds([...selectedIds, existingLabel.id]);
      }
      setNewName("");
      return;
    }

    if (nameError !== null) {
      setNewNameError(toNameErrorText(nameError));
      return;
    }

    if (isAtMax) {
      setNewNameError(t("picker.maxReached", { max: MAX_LABELS_PER_CASE }));
      return;
    }

    createLabel.mutate({ name: newName.trim(), color: DEFAULT_LABEL_COLOR });
  };

  const handleSave = (): void => {
    if (checkHasSameLabelIds(selectedIds, labels)) {
      setIsEditing(false);
      return;
    }

    saveLabels.mutate(selectedIds);
  };

  if (!isEditing) {
    return (
      <section className={styles.picker} aria-label={t("picker.title")}>
        <div className={styles.summary}>
          <DSText weight="medium" component="span">
            {t("picker.title")}
          </DSText>
          {labels.length === 0 ? (
            <DSText color="muted" size="sm" component="span">
              {t("picker.none")}
            </DSText>
          ) : (
            <LabelChips labels={labels} />
          )}
          {canEdit && (
            <DSButton type="ghost" size="sm" icon="label" onClick={startEditing}>
              {t("picker.edit")}
            </DSButton>
          )}
        </div>
      </section>
    );
  }

  return (
    <section className={styles.picker} aria-label={t("picker.title")}>
      <DSStack gap={3}>
        {projectLabels.isError && <DSAlert color="danger">{t("picker.loadError")}</DSAlert>}
        <DSMultiSelect<string>
          label={t("picker.field")}
          value={selectedIds}
          options={buildLabelOptions(availableLabels, labels)}
          onChange={setSelectedIds}
          placeholder={t("picker.placeholder")}
          description={isAtMax ? t("picker.maxReached", { max: MAX_LABELS_PER_CASE }) : undefined}
          nothingFoundLabel={t("picker.noMatch")}
          maxValues={MAX_LABELS_PER_CASE}
          isDisabled={projectLabels.isPending || saveLabels.isPending}
        />
        <div className={styles.newLabel}>
          <div className={styles.newLabelInput}>
            <DSInput
              label={t("picker.newLabel")}
              value={newName}
              onChange={handleNewNameChange}
              placeholder={t("picker.newLabelPlaceholder")}
              error={newNameError ?? undefined}
              autoComplete="off"
              isDisabled={saveLabels.isPending}
            />
          </div>
          <DSButton
            type="default"
            icon="plus"
            isLoading={createLabel.isPending}
            isDisabled={newName.trim() === "" || projectLabels.isPending || saveLabels.isPending}
            onClick={handleCreate}
          >
            {t("picker.create")}
          </DSButton>
        </div>
        <DSGroup gap={2} justify="end">
          <DSButton
            type="default"
            isDisabled={saveLabels.isPending}
            onClick={() => {
              setIsEditing(false);
            }}
          >
            {t("picker.cancel")}
          </DSButton>
          <DSButton
            type="primary"
            icon="check"
            isLoading={saveLabels.isPending}
            isDisabled={createLabel.isPending}
            onClick={handleSave}
          >
            {saveLabels.isPending ? t("picker.saving") : t("picker.save")}
          </DSButton>
        </DSGroup>
      </DSStack>
    </section>
  );
};
