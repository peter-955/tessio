"use client";

import {
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSModal,
  DSSelect,
  DSSkeleton,
  DSStack,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetSharedSteps } from "../../hooks/queries/use-get-shared-steps";
import { listInsertableSharedSteps } from "../../utils/shared-step-form.util";
import { buildSharedStepsPath } from "../../utils/shared-step-path.util";
import { SharedStepActions } from "../shared-step-actions/shared-step-actions";

interface Props {
  projectKey: string;
  onClose: () => void;
  onInsert: (sharedStepKey: string) => void;
}

export const SharedStepPickerModal: FC<Props> = ({ projectKey, onClose, onInsert }) => {
  const { t } = useTranslation("sharedSteps");
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const { data, isPending, isError, isFetching, refetch } = useGetSharedSteps(projectKey, true);
  const sharedSteps = listInsertableSharedSteps(data ?? []);
  const selectedStep = sharedSteps.find((sharedStep) => sharedStep.key === selectedKey) ?? null;
  const options = sharedSteps.map((sharedStep): DSSelectOption<string> => {
    return { value: sharedStep.key, label: `${sharedStep.title} (${sharedStep.key})` };
  });

  const renderBody = (): ReactNode => {
    if (isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("picker.loading")}>
          <DSSkeleton lineCount={3} />
        </div>
      );
    }

    if (isError) {
      return (
        <DSErrorState
          title={t("picker.loadError")}
          retryLabel={t("picker.retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (sharedSteps.length === 0) {
      return (
        <DSEmptyState
          title={t("picker.emptyTitle")}
          description={t("picker.emptyDescription")}
          icon="sharedSteps"
          size="sm"
          action={
            <DSButtonLink href={buildSharedStepsPath(projectKey)} type="default">
              {t("picker.openLibrary")}
            </DSButtonLink>
          }
        />
      );
    }

    return (
      <DSStack gap={4}>
        <DSSelect<string>
          label={t("picker.select")}
          placeholder={t("picker.selectPlaceholder")}
          value={selectedKey}
          options={options}
          onChange={setSelectedKey}
          nothingFoundLabel={t("picker.nothingFound")}
          isSearchable
          isRequired
        />
        {selectedStep !== null && (
          <DSStack gap={2}>
            <DSText size="sm" color="muted">
              {t("picker.preview", { count: selectedStep.currentVersion.steps.length })}
            </DSText>
            <SharedStepActions
              actions={selectedStep.currentVersion.steps}
              ariaLabel={t("reference.stepsOf", { title: selectedStep.title })}
            />
          </DSStack>
        )}
      </DSStack>
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("picker.title")}
      action={{
        label: t("picker.insert"),
        icon: "plus",
        isDisabled: selectedStep === null,
        onClick: () => {
          if (selectedStep !== null) {
            onInsert(selectedStep.key);
          }
        },
      }}
    >
      {renderBody()}
    </DSModal>
  );
};
