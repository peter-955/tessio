"use client";

import {
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
  DSText,
} from "@/components/design-system";
import type { RunDetail } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetRunLog } from "../../hooks/queries/use-get-run-log";
import { RUN_LOG_UPLOAD_WINDOW_IN_MILLISECONDS } from "../../typing/constants/run-log.constant";
import type { RunLogSection } from "../../typing/types/run-log.type";
import { groupRunLogEntries, sumTokens } from "../../utils/run-log.util";
import { RunLogEntryRow } from "../run-log-entry/run-log-entry";
import styles from "./run-log.module.scss";

interface Props {
  projectKey: string;
  run: RunDetail;
}

const LOADING_LINE_COUNT = 6;

export const RunLogView: FC<Props> = ({ projectKey, run }) => {
  const { t } = useTranslation("runs");
  const { data, isPending, isError, isFetching, refetch, dataUpdatedAt } = useGetRunLog(
    projectKey,
    run.id,
  );
  const caseByTestCaseId = new Map(
    run.cases.map((runCase) => {
      return [runCase.testCaseId, runCase];
    }),
  );

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("log.loading")}>
        <DSSkeleton lineCount={LOADING_LINE_COUNT} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("log.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  if (data.receivedAt === null) {
    const isLate =
      run.finishedAt !== null &&
      dataUpdatedAt - Date.parse(run.finishedAt) > RUN_LOG_UPLOAD_WINDOW_IN_MILLISECONDS;

    return <DSEmptyState title={isLate ? t("log.missing") : t("log.pending")} icon="file" />;
  }

  const startAt = data.entries[0]?.at ?? data.receivedAt;
  const caseCount = run.cases.length;
  const totalTokens = data.usage === null ? 0 : sumTokens(data.usage);

  const buildSectionTitle = (section: RunLogSection): string => {
    if (section.phase === "setup") {
      return t("log.setup");
    }
    if (section.phase === "wrap_up") {
      return t("log.wrapUp");
    }
    const runCase =
      section.testCaseId === null ? undefined : caseByTestCaseId.get(section.testCaseId);

    return runCase === undefined ? t("log.unknownCase") : `${runCase.code} · ${runCase.title}`;
  };

  return (
    <DSStack gap={4}>
      <DSText size="sm" color="muted">
        {caseCount > 0
          ? t("log.tokensPerCase", {
              total: totalTokens.toLocaleString(),
              perCase: Math.round(totalTokens / caseCount).toLocaleString(),
            })
          : t("log.tokens", { total: totalTokens.toLocaleString() })}
      </DSText>
      {data.isCut && (
        <DSText size="sm" color="warning">
          {t("log.cut")}
        </DSText>
      )}
      {groupRunLogEntries(data.entries).map((section) => {
        return (
          <section
            key={section.id}
            className={styles.section}
            aria-label={buildSectionTitle(section)}
          >
            <h3 className={styles.title}>{buildSectionTitle(section)}</h3>
            <ol className={styles.entries}>
              {section.entries.map((entry) => {
                return <RunLogEntryRow key={entry.position} entry={entry} startAt={startAt} />;
              })}
            </ol>
          </section>
        );
      })}
    </DSStack>
  );
};
