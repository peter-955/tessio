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
import { SuiteFormModal } from "./components/suite-form-modal/suite-form-modal";
import { SuiteTable } from "./components/suite-table/suite-table";
import { useGetSuites } from "./hooks/queries/use-get-suites";
import styles from "./suites.module.scss";
import { LOADING_ROW_COUNT } from "./typing/constants/suite.constant";
import { buildSuitePath } from "./utils/suite-path.util";
import { checkCanEditSuites } from "./utils/suite-permission.util";

export const SuitesPage: FC = () => {
  const { t } = useTranslation("suites");
  const router = useRouter();
  const project = useCurrentProject();
  const [isArchivedShown, setIsArchivedShown] = useState(false);
  const [isCreateOpened, setIsCreateOpened] = useState(false);
  const { data, isPending, isError, isFetching, refetch } = useGetSuites(
    project.key,
    isArchivedShown,
  );
  const canEdit = checkCanEditSuites(project);

  const openCreate = (): void => {
    setIsCreateOpened(true);
  };

  const createButton = canEdit && (
    <DSButton type="primary" icon="plus" onClick={openCreate}>
      {t("list.newSuite")}
    </DSButton>
  );

  const renderSuites = (): ReactNode => {
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
          icon="suites"
          action={createButton}
        />
      );
    }

    return <SuiteTable projectKey={project.key} suites={data} />;
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
        {renderSuites()}
      </DSStack>
      {isCreateOpened && (
        <SuiteFormModal
          projectKey={project.key}
          suite={null}
          onClose={() => {
            setIsCreateOpened(false);
          }}
          onCreated={(suite) => {
            router.push(buildSuitePath(project.key, suite.id));
          }}
        />
      )}
    </>
  );
};
