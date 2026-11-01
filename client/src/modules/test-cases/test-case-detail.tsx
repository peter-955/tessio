"use client";

import { DSButtonLink, DSEmptyState, DSErrorState, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TestCaseDetailView } from "./components/test-case-detail-view/test-case-detail-view";
import { useGetTestCase } from "./hooks/queries/use-get-test-case";
import { CASE_CODE_PATTERN, NOT_FOUND_STATUS } from "./typing/constants/test-case.constant";
import type { TestCaseDetailTab } from "./typing/enums/test-case-detail-tab.enum";
import type { TestCaseDetail } from "./typing/types/test-case.type";
import { buildTestCasesPath } from "./utils/test-case-path.util";

interface Props {
  caseCode: string;
  initialTab: TestCaseDetailTab;
}

export const TestCaseDetailPage: FC<Props> = ({ caseCode, initialTab }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const normalizedCode = caseCode.toUpperCase();
  const isValidCode = CASE_CODE_PATTERN.test(normalizedCode);
  const { data, error, isPending, isError, isFetching, refetch } = useGetTestCase(
    project.key,
    normalizedCode,
    isValidCode,
  );

  if (!isValidCode || error?.status === NOT_FOUND_STATUS) {
    return (
      <DSEmptyState
        title={t("detail.notFound.title")}
        description={t("detail.notFound.description")}
        icon="testCases"
        action={
          <DSButtonLink href={buildTestCasesPath(project.key)} type="default">
            {t("actions.back")}
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

  const handleReload = async (): Promise<TestCaseDetail | undefined> => {
    const result = await refetch();

    return result.data;
  };

  return (
    <TestCaseDetailView
      key={data.id}
      detail={data}
      initialTab={initialTab}
      onReload={handleReload}
    />
  );
};
