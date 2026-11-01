"use client";

import { DSAlert, DSButtonLink } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkCanEditTestCases } from "@/modules/test-cases/utils/test-case-capability.util";
import { buildNewTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CriterionTrace } from "../../typing/types/traceability.type";
import { listUncoveredCriteria } from "../../utils/matrix.util";

interface Props {
  criteria: readonly CriterionTrace[];
  projectKey: string;
  jiraKey: string;
}

export const UncoveredCriteriaBanner: FC<Props> = ({ criteria, projectKey, jiraKey }) => {
  const { t } = useTranslation("traceability");
  const project = useCurrentProject();
  const uncoveredCriteria = listUncoveredCriteria(criteria);

  if (uncoveredCriteria.length === 0) {
    return null;
  }

  const codes = uncoveredCriteria
    .map((criterion) => {
      return criterion.code;
    })
    .join(", ");

  return (
    <DSAlert
      color="warning"
      title={t("uncovered.title", { count: uncoveredCriteria.length })}
      action={
        checkCanEditTestCases(project) && (
          <DSButtonLink href={buildNewTestCasePath(projectKey, jiraKey)} type="default" icon="plus">
            {t("uncovered.action")}
          </DSButtonLink>
        )
      }
    >
      {t("uncovered.description", { codes })}
    </DSAlert>
  );
};
