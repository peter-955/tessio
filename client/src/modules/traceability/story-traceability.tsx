"use client";

import {
  DSButtonLink,
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSStack,
  DSTraceabilityMatrix,
  type DSTraceabilityMatrixLabels,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useFormatDay } from "@/modules/stories/hooks/use-format-day";
import { checkCanEditTestCases } from "@/modules/test-cases/utils/test-case-capability.util";
import { buildNewTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { CoverageSummary } from "./components/coverage-summary/coverage-summary";
import { StoryTraceabilitySkeleton } from "./components/story-traceability-skeleton/story-traceability-skeleton";
import { UncoveredCriteriaBanner } from "./components/uncovered-criteria-banner/uncovered-criteria-banner";
import { useGetTraceability } from "./hooks/queries/use-get-traceability";
import type { MatrixCaseLabels } from "./typing/types/matrix-case-labels.type";
import { buildMatrixCases, buildMatrixCriteria } from "./utils/matrix.util";

interface Props {
  jiraKey: string;
}

export const StoryTraceability: FC<Props> = ({ jiraKey }) => {
  const { t } = useTranslation("traceability");
  const project = useCurrentProject();
  const formatDay = useFormatDay();
  const { data, isPending, isError, isFetching, refetch } = useGetTraceability(
    project.key,
    jiraKey,
  );

  if (isPending) {
    return <StoryTraceabilitySkeleton />;
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

  if (data.criteria.length === 0) {
    return (
      <DSEmptyState
        title={t("empty.noCriteria.title")}
        description={t("empty.noCriteria.description")}
        icon="file"
      />
    );
  }

  const newCaseLink = checkCanEditTestCases(project) && (
    <DSButtonLink href={buildNewTestCasePath(project.key, jiraKey)} type="default" icon="plus">
      {t("uncovered.action")}
    </DSButtonLink>
  );
  const caseLabels: MatrixCaseLabels = {
    notReady: { draft: t("matrix.notReady.draft"), in_review: t("matrix.notReady.in_review") },
    needsReview: t("matrix.needsReview"),
  };
  const matrixLabels: DSTraceabilityMatrixLabels = {
    caption: t("matrix.caption", { jiraKey }),
    criterion: t("matrix.criterion"),
    status: t("matrix.status"),
    notLinked: t("matrix.notLinked"),
    resultStatuses: {
      passed: t("resultStatus.passed"),
      failed: t("resultStatus.failed"),
      blocked: t("resultStatus.blocked"),
      skipped: t("resultStatus.skipped"),
      not_run: t("resultStatus.not_run"),
    },
    criterionStatuses: {
      uncovered: t("criterionStatus.uncovered"),
      not_run: t("criterionStatus.not_run"),
      passed: t("criterionStatus.passed"),
      failed: t("criterionStatus.failed"),
      blocked: t("criterionStatus.blocked"),
    },
  };

  return (
    <DSStack gap={4}>
      <UncoveredCriteriaBanner
        criteria={data.criteria}
        projectKey={project.key}
        jiraKey={jiraKey}
      />
      <DSCard title={t("title")}>
        <DSStack gap={4}>
          <CoverageSummary coverage={data.coverage} />
          {data.cases.length === 0 ? (
            <DSEmptyState
              title={t("empty.noCases.title")}
              description={t("empty.noCases.description")}
              icon="testCases"
              action={newCaseLink}
            />
          ) : (
            <DSTraceabilityMatrix
              criteria={buildMatrixCriteria(data.criteria, (removedAt) => {
                return t("matrix.removed", { date: formatDay(removedAt) });
              })}
              cases={buildMatrixCases(data.cases, project.key, caseLabels)}
              labels={matrixLabels}
            />
          )}
        </DSStack>
      </DSCard>
    </DSStack>
  );
};
