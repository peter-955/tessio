"use client";

import {
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSkeleton,
  DSStack,
  DSSwitch,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useRouter } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { SharedStepFormModal } from "./components/shared-step-form-modal/shared-step-form-modal";
import { SharedStepTable } from "./components/shared-step-table/shared-step-table";
import { useGetSharedSteps } from "./hooks/queries/use-get-shared-steps";
import styles from "./shared-steps.module.scss";
import { LOADING_ROW_COUNT } from "./typing/constants/shared-step.constant";
import { buildSharedStepPath } from "./utils/shared-step-path.util";
import { checkCanEditSharedSteps } from "./utils/shared-step-permission.util";

export const SharedStepsPage: FC = () => {
  const { t } = useTranslation("sharedSteps");
  const router = useRouter();
  const project = useCurrentProject();
  const [isArchivedShown, setIsArchivedShown] = useState(false);
  const [isCreateOpened, setIsCreateOpened] = useState(false);
  const { data, isPending, isError, isFetching, refetch } = useGetSharedSteps(
    project.key,
    isArchivedShown,
  );
  const canEdit = checkCanEditSharedSteps(project);

  const createButton = canEdit && (
    <DSButton
      type="primary"
      icon="plus"
      onClick={() => {
        setIsCreateOpened(true);
      }}
    >
      {t("list.newSharedStep")}
    </DSButton>
  );

  const renderSharedSteps = (): ReactNode => {
    if (isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("list.loading")}>
          <DSSkeleton lineCount={LOADING_ROW_COUNT} height={40} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("list.loadError")}
          retryLabel={t("list.retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (data.length === 0) {
      return (
        <DSEmptyState
          title={t("list.emptyTitle")}
          description={canEdit ? t("list.emptyDescription") : t("list.emptyReadOnlyDescription")}
          icon="sharedSteps"
          action={createButton}
        />
      );
    }

    return <SharedStepTable projectKey={project.key} sharedSteps={data} />;
  };

  return (
    <>
      <DSPageHeader
        title={t("page.title")}
        description={t("page.description")}
        actions={createButton}
      />
      <DSStack gap={4}>
        <div className={styles.toolbar}>
          <DSSwitch
            label={t("list.showArchived")}
            isChecked={isArchivedShown}
            onChange={setIsArchivedShown}
          />
        </div>
        {renderSharedSteps()}
      </DSStack>
      {isCreateOpened && (
        <SharedStepFormModal
          projectKey={project.key}
          sharedStep={null}
          onClose={() => {
            setIsCreateOpened(false);
          }}
          onCreated={(sharedStep) => {
            router.push(buildSharedStepPath(project.key, sharedStep.key));
          }}
        />
      )}
    </>
  );
};
