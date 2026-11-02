"use client";

import { DSButton, DSEmptyState, DSErrorState, DSSkeleton } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetPlans } from "../../hooks/queries/use-get-plans";
import type { PlanStatusFilter } from "../../typing/types/plan-status-filter.type";
import { PlanTable } from "../plan-table/plan-table";

interface Props {
  projectKey: string;
  status: PlanStatusFilter;
  createAction: ReactNode;
  onShowAll: () => void;
}

export const PlanList: FC<Props> = ({ projectKey, status, createAction, onShowAll }) => {
  const { t } = useTranslation("plans");
  const { data, isPending, isError, isFetching, refetch } = useGetPlans(projectKey, status);

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
        title={t("list.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  if (data.length === 0) {
    if (status !== "all") {
      return (
        <DSEmptyState
          title={t("list.empty.noMatch")}
          description={t("list.empty.noMatchDescription")}
          icon="search"
          action={
            <DSButton type="default" onClick={onShowAll}>
              {t("list.empty.showAll")}
            </DSButton>
          }
        />
      );
    }

    return (
      <DSEmptyState
        title={t("list.empty.title")}
        description={t("list.empty.description")}
        icon="plans"
        action={createAction}
      />
    );
  }

  return <PlanTable projectKey={projectKey} plans={data} />;
};
