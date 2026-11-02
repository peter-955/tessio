"use client";

import { DSErrorState, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { SuiteDetailView } from "./components/suite-detail-view/suite-detail-view";
import { SuiteNotFound } from "./components/suite-not-found/suite-not-found";
import { useGetSuite } from "./hooks/queries/use-get-suite";
import { NOT_FOUND_STATUS, SUITE_ID_PATTERN } from "./typing/constants/suite.constant";

interface Props {
  suiteId: string;
}

const LOADING_LINE_COUNT = 8;

export const SuiteDetailPage: FC<Props> = ({ suiteId }) => {
  const { t } = useTranslation("suites");
  const project = useCurrentProject();
  const isValidId = SUITE_ID_PATTERN.test(suiteId);
  const { data, error, isPending, isError, isFetching, refetch } = useGetSuite(
    project.key,
    suiteId,
    isValidId,
  );

  if (!isValidId || error?.status === NOT_FOUND_STATUS) {
    return <SuiteNotFound projectKey={project.key} />;
  }

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("detail.loading")}>
        <DSSkeleton lineCount={LOADING_LINE_COUNT} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("detail.loadError")}
        retryLabel={t("detail.retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  return <SuiteDetailView key={data.id} suite={data} />;
};
