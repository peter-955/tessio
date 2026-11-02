"use client";

import { DSButtonLink, DSEmptyState, DSErrorState, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PlanBlockersCard } from "./components/plan-blockers-card/plan-blockers-card";
import { PlanCasesCard } from "./components/plan-cases-card/plan-cases-card";
import { PlanHeader } from "./components/plan-header/plan-header";
import { PlanItemsCard } from "./components/plan-items-card/plan-items-card";
import { PlanProgressCard } from "./components/plan-progress-card/plan-progress-card";
import { useGetPlan } from "./hooks/queries/use-get-plan";
import styles from "./plan-detail.module.scss";
import { NOT_FOUND_STATUS } from "./typing/constants/plan.constant";
import { buildPlansPath } from "./utils/plan-path.util";

interface Props {
  planId: string;
}

export const PlanDetailPage: FC<Props> = ({ planId }) => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();
  const isValidId = UUID_PATTERN.test(planId);
  const { data, error, isPending, isError, isFetching, refetch } = useGetPlan(project.key, planId);

  if (!isValidId || error?.status === NOT_FOUND_STATUS) {
    return (
      <DSEmptyState
        title={t("detail.notFoundTitle")}
        description={t("detail.notFoundDescription")}
        icon="plans"
        action={
          <DSButtonLink href={buildPlansPath(project.key)} type="default">
            {t("detail.back")}
          </DSButtonLink>
        }
      />
    );
  }

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={8} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("detail.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  return (
    <>
      <PlanHeader plan={data} />
      <div className={styles.grid}>
        <div className={styles.column}>
          <PlanProgressCard plan={data} />
          <PlanCasesCard cases={data.progress.cases} />
        </div>
        <div className={styles.column}>
          <PlanBlockersCard failures={data.progress.failures} gaps={data.progress.gaps} />
          <PlanItemsCard items={data.items} />
        </div>
      </div>
    </>
  );
};
