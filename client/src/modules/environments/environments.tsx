"use client";

import {
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSGroup,
  DSSkeleton,
  DSSwitch,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useHasProjectCapability } from "@/components/project-context/hooks/use-has-project-capability";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { DeleteEnvironmentModal } from "./components/delete-environment-modal/delete-environment-modal";
import { EnvironmentModal } from "./components/environment-modal/environment-modal";
import { EnvironmentsTable } from "./components/environments-table/environments-table";
import styles from "./environments.module.scss";
import { usePostArchiveEnvironment } from "./hooks/mutations/use-post-archive-environment";
import { usePostUnarchiveEnvironment } from "./hooks/mutations/use-post-unarchive-environment";
import { ENVIRONMENT_SKELETON_ROW_COUNT } from "./typing/constants/environment.constant";
import type { EnvironmentModalState } from "./typing/types/environment-modal-state.type";
import type { Environment } from "./typing/types/environment.type";

export const EnvironmentsPanel: FC = () => {
  const { t } = useTranslation("environments");
  const project = useCurrentProject();
  const canManage = useHasProjectCapability("environment.manage");
  const { showSuccessToast } = useShowToast();
  const [isShowingArchived, setIsShowingArchived] = useState(false);
  const [modalState, setModalState] = useState<EnvironmentModalState | null>(null);
  const [deletingEnvironment, setDeletingEnvironment] = useState<Environment | null>(null);
  const {
    data: environments,
    isPending,
    isError,
    isFetching,
    refetch,
  } = useGetEnvironments(project.key, { isIncludingArchived: isShowingArchived });
  const archiveEnvironment = usePostArchiveEnvironment(project.key, {
    onSuccess: () => {
      showSuccessToast(t("toasts.archived"));
    },
  });
  const unarchiveEnvironment = usePostUnarchiveEnvironment(project.key, {
    onSuccess: () => {
      showSuccessToast(t("toasts.unarchived"));
    },
  });

  const openCreateModal = (): void => {
    setModalState({ mode: "create" });
  };

  const openEditModal = (environment: Environment): void => {
    setModalState({ mode: "edit", environment });
  };

  const closeModal = (): void => {
    setModalState(null);
  };

  const closeDeleteModal = (): void => {
    setDeletingEnvironment(null);
  };

  const handleArchive = (environment: Environment): void => {
    archiveEnvironment.mutate(environment.id);
  };

  const handleUnarchive = (environment: Environment): void => {
    unarchiveEnvironment.mutate(environment.id);
  };

  const addButton = canManage && (
    <DSButton type="primary" icon="plus" onClick={openCreateModal}>
      {t("actions.add")}
    </DSButton>
  );

  const renderContent = (): ReactNode => {
    if (isPending) {
      return (
        <div
          className={styles.loading}
          role="status"
          aria-busy="true"
          aria-label={t("table.loading")}
        >
          <DSSkeleton height={36} lineCount={ENVIRONMENT_SKELETON_ROW_COUNT} />
        </div>
      );
    }

    if (isError || environments === undefined) {
      return (
        <DSErrorState
          title={t("errors.loadFailed")}
          retryLabel={t("actions.retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (environments.length === 0) {
      return (
        <DSEmptyState
          title={t("empty.title")}
          description={t("empty.description")}
          icon="environments"
          action={addButton}
        />
      );
    }

    return (
      <EnvironmentsTable
        environments={environments}
        defaultEnvironmentId={project.defaultEnvironmentId ?? null}
        canManage={canManage}
        onEdit={openEditModal}
        onArchive={handleArchive}
        onUnarchive={handleUnarchive}
        onDelete={setDeletingEnvironment}
      />
    );
  };

  return (
    <section>
      <DSGroup justify="between" isWrapping className={styles.toolbar}>
        <DSSwitch
          label={t("showArchived")}
          isChecked={isShowingArchived}
          onChange={setIsShowingArchived}
        />
        {addButton}
      </DSGroup>
      {renderContent()}
      {modalState !== null && (
        <EnvironmentModal
          projectKey={project.key}
          environment={modalState.mode === "edit" ? modalState.environment : null}
          onClose={closeModal}
        />
      )}
      {deletingEnvironment !== null && (
        <DeleteEnvironmentModal
          projectKey={project.key}
          environment={deletingEnvironment}
          onClose={closeDeleteModal}
        />
      )}
    </section>
  );
};
