"use client";

import {
  DSAlert,
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
} from "@/components/design-system";
import { buildRunPath } from "@/modules/runs/utils/run-path.util";
import type { SuiteDetail } from "@/modules/suites/typing/types/suite.type";
import {
  findSuiteCaseSkipReason,
  listRunnableSuiteCases,
  listSkippedSuiteCases,
} from "@/modules/suites/utils/suite-cases.util";
import { buildSuitePath } from "@/modules/suites/utils/suite-path.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CasePickerItem } from "../../typing/types/case-picker-item.type";
import { CasePicker } from "../case-picker/case-picker";
import styles from "./suite-case-picker.module.scss";

interface Props {
  projectKey: string;
  suite: SuiteDetail | undefined;
  isPending: boolean;
  isError: boolean;
  isFetching: boolean;
  onRetry: () => void;
  selectedIds: readonly string[];
  onChange: (selectedIds: string[]) => void;
  isDisabled: boolean;
}

export const SuiteCasePicker: FC<Props> = ({
  projectKey,
  suite,
  isPending,
  isError,
  isFetching,
  onRetry,
  selectedIds,
  onChange,
  isDisabled,
}) => {
  const { t } = useTranslation("suites");

  if (isPending) {
    return <DSSkeleton height={48} lineCount={3} />;
  }

  if (isError || suite === undefined) {
    return (
      <DSErrorState
        title={t("manualRun.loadError")}
        retryLabel={t("manualRun.retry")}
        isRetrying={isFetching}
        onRetry={onRetry}
      />
    );
  }

  const runnableCases = listRunnableSuiteCases(suite.cases);
  const skippedCases = listSkippedSuiteCases(suite.cases);
  const items = runnableCases.map((suiteCase): CasePickerItem => {
    return {
      id: suiteCase.testCaseId,
      label: `${suiteCase.code} · ${suiteCase.title} · ${suiteCase.storyJiraKey}`,
    };
  });

  return (
    <DSStack gap={4}>
      {suite.runningRun !== null && (
        <DSAlert
          color="warning"
          title={t("manualRun.runningTitle")}
          action={
            <DSButtonLink href={buildRunPath(projectKey, suite.runningRun.id)} size="sm">
              {t("manualRun.openRun")}
            </DSButtonLink>
          }
        >
          {t("manualRun.runningDescription")}
        </DSAlert>
      )}
      {items.length === 0 ? (
        <DSEmptyState
          title={t("manualRun.noRunnableTitle")}
          description={t("manualRun.noRunnableDescription")}
          icon="suites"
          size="sm"
          action={
            <DSButtonLink href={buildSuitePath(projectKey, suite.id)}>
              {t("manualRun.openSuite")}
            </DSButtonLink>
          }
        />
      ) : (
        <CasePicker
          cases={items}
          selectedIds={selectedIds}
          onChange={onChange}
          isDisabled={isDisabled}
        />
      )}
      {skippedCases.length > 0 && (
        <DSAlert color="info" title={t("manualRun.skippedTitle", { count: skippedCases.length })}>
          <ul className={styles.skipped}>
            {skippedCases.map((suiteCase) => {
              const reason = findSuiteCaseSkipReason(suiteCase) ?? "not_ready";

              return (
                <li key={suiteCase.testCaseId}>
                  {t("manualRun.skippedCase", {
                    code: suiteCase.code,
                    title: suiteCase.title,
                    reason: t(`skipReason.${reason}`),
                  })}
                </li>
              );
            })}
          </ul>
        </DSAlert>
      )}
    </DSStack>
  );
};
