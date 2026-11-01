"use client";

import { DSErrorState, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { RunDetailView } from "./components/run-detail-view/run-detail-view";
import { RunNotFound } from "./components/run-not-found/run-not-found";
import { useGetRun } from "./hooks/queries/use-get-run";
import { NOT_FOUND_STATUS, RUN_ID_PATTERN } from "./typing/constants/run.constant";
import type { RunDetailTab } from "./typing/enums/run-detail-tab.enum";

interface Props {
  runId: string;
  initialTab: RunDetailTab;
  actions?: ReactNode;
}

const LOADING_LINE_COUNT = 8;

export const RunDetailPage: FC<Props> = ({ runId, initialTab, actions }) => {
  const { t } = useTranslation("runs");
  const project = useCurrentProject();
  const isValidId = RUN_ID_PATTERN.test(runId);
  const { data, error, isPending, isError, isFetching, refetch } = useGetRun(
    project.key,
    runId,
    isValidId,
  );

  if (!isValidId || error?.status === NOT_FOUND_STATUS) {
    return <RunNotFound projectKey={project.key} />;
  }

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("loading")}>
        <DSSkeleton lineCount={LOADING_LINE_COUNT} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  return (
    <RunDetailView
      key={data.id}
      projectKey={project.key}
      run={data}
      initialTab={initialTab}
      actions={actions}
    />
  );
};
