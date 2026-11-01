"use client";

import { DSButton, DSEmptyState, DSErrorState, DSSkeleton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetFailures } from "../../hooks/queries/use-get-failures";
import type { FailureFilters } from "../../typing/types/failure-filters.type";
import { checkHasFailureFilters } from "../../utils/failure-filters.util";
import { FailureTable } from "../failure-table/failure-table";

interface Props {
  projectKey: string;
  filters: FailureFilters;
  onClearFilters: () => void;
}

export const FailureList: FC<Props> = ({ projectKey, filters, onClearFilters }) => {
  const { t } = useTranslation("failures");
  const { data, isPending, isError, isFetching, refetch } = useGetFailures(projectKey, filters);

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
    if (checkHasFailureFilters(filters)) {
      return (
        <DSEmptyState
          title={t("empty.noMatch")}
          description={t("empty.noMatchDescription")}
          icon="search"
          action={
            <DSButton type="default" onClick={onClearFilters}>
              {t("empty.clearFilters")}
            </DSButton>
          }
        />
      );
    }

    return (
      <DSEmptyState title={t("empty.title")} description={t("empty.description")} icon="failures" />
    );
  }

  return <FailureTable projectKey={projectKey} failures={data} />;
};
