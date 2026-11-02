"use client";

import { DSBadge } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { buildRunPath } from "@/modules/traceability/utils/run-path.util";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLAN_CASE_STATUS_COLORS } from "../../typing/constants/plan.constant";
import type { PlanCase } from "../../typing/types/plan.type";
import { selectPlanCaseStatus } from "../../utils/plan-progress.util";

interface Props {
  planCase: PlanCase;
}

export const PlanCaseResult: FC<Props> = ({ planCase }) => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();
  const status = selectPlanCaseStatus(planCase);
  const badge = (
    <DSBadge color={PLAN_CASE_STATUS_COLORS[status]} hasDot>
      {t(`caseStatus.${status}`)}
    </DSBadge>
  );

  if (planCase.latestResult === null) {
    return badge;
  }

  return <Link href={buildRunPath(project.key, planCase.latestResult.runId)}>{badge}</Link>;
};
