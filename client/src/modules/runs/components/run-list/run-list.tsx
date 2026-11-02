"use client";

import {
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
  DSText,
} from "@/components/design-system";
import { RunsTable } from "@/components/runs-table/runs-table";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetRuns } from "../../hooks/queries/use-get-runs";
import {
  LOADING_ROW_COUNT,
  NOT_FOUND_STATUS,
  RUN_LIST_LIMIT,
} from "../../typing/constants/run.constant";
import type { RunFilters } from "../../typing/types/run.type";
import { checkHasRunFilters } from "../../utils/run-filters.util";

interface Props {
  projectKey: string;
  filters: RunFilters;
  onClearFilters: () => void;
}

export const RunList: FC<Props> = ({ projectKey, filters, onClearFilters }) => {
  const { t } = useTranslation("runs");
  const { data, error, isPending, isError, isFetching, refetch } = useGetRuns(projectKey, filters);
  const isUnknownStory =
    error?.status === NOT_FOUND_STATUS && (filters.storyKey !== null || filters.suiteId !== null);

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("loading")}>
        <DSSkeleton lineCount={LOADING_ROW_COUNT} height={40} />
      </div>
    );
  }

  const filteredEmptyState = (
    <DSEmptyState
      title={t("empty.filteredTitle")}
      description={t("empty.filteredDescription")}
      icon="search"
      action={
        <DSButton type="default" onClick={onClearFilters}>
          {t("filters.clear")}
        </DSButton>
      }
    />
  );

  if (isUnknownStory) {
    return filteredEmptyState;
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
    if (checkHasRunFilters(filters)) {
      return filteredEmptyState;
    }

    return (
      <DSEmptyState title={t("empty.title")} description={t("empty.description")} icon="runs" />
    );
  }

  return (
    <DSStack gap={3}>
      <RunsTable runs={data} projectKey={projectKey} isStoryColumnShown />
      {data.length === RUN_LIST_LIMIT && (
        <DSText size="sm" color="muted">
          {t("limitNotice", { count: RUN_LIST_LIMIT })}
        </DSText>
      )}
    </DSStack>
  );
};
