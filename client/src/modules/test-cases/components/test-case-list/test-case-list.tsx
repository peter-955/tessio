"use client";

import { DSButton, DSEmptyState, DSErrorState, DSSkeleton } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetCaseLatestResults } from "../../hooks/queries/use-get-case-latest-results";
import { useGetTestCases } from "../../hooks/queries/use-get-test-cases";
import type { TestCaseFilters } from "../../typing/types/test-case-filters.type";
import { mapLatestResultByCaseId } from "../../utils/latest-result.util";
import { checkHasTestCaseFilters } from "../../utils/test-case-filters.util";
import { TestCaseTable } from "../test-case-table/test-case-table";

interface Props {
  projectKey: string;
  filters: TestCaseFilters;
  isStoryColumnShown: boolean;
  emptyActions?: ReactNode;
  onClearFilters: () => void;
}

export const TestCaseList: FC<Props> = ({
  projectKey,
  filters,
  isStoryColumnShown,
  emptyActions,
  onClearFilters,
}) => {
  const { t } = useTranslation("testCases");
  const { data, isPending, isError, isFetching, refetch } = useGetTestCases(projectKey, filters);
  const latestResults = useGetCaseLatestResults(projectKey, filters.storyKey);
  const latestResultByCaseId =
    latestResults.isError || latestResults.data === undefined
      ? undefined
      : mapLatestResultByCaseId(latestResults.data);

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={6} />
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

  if (data.length === 0) {
    if (checkHasTestCaseFilters(filters, !isStoryColumnShown)) {
      return (
        <DSEmptyState
          title={t("empty.noMatch")}
          description={t("empty.noMatchDescription")}
          icon="search"
          action={
            <DSButton type="default" onClick={onClearFilters}>
              {t("actions.clearFilters")}
            </DSButton>
          }
        />
      );
    }

    return (
      <DSEmptyState
        title={t("empty.title")}
        description={t("empty.description")}
        icon="testCases"
        action={emptyActions}
      />
    );
  }

  return (
    <TestCaseTable
      projectKey={projectKey}
      testCases={data}
      isStoryColumnShown={isStoryColumnShown}
      latestResultByCaseId={latestResultByCaseId}
    />
  );
};
