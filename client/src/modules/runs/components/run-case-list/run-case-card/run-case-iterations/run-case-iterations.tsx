"use client";

import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import { DSIcon, DSText, DSTitle } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { SuspectedCause } from "@/components/suspected-cause/suspected-cause";
import { IterationValues } from "@/modules/data-rows/components/iteration-values/iteration-values";
import { formatIterationNumber } from "@/modules/data-rows/utils/parameter-text.util";
import { useFormatDuration } from "@/shared/hooks/use-format-duration";
import type { RunCase, RunStatus } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { resolveCaseOutcome } from "../../../../utils/run-outcome.util";
import { RunCaseSteps } from "../run-case-steps/run-case-steps";
import styles from "./run-case-iterations.module.scss";

interface Props {
  projectKey: string;
  runCase: RunCase;
  runStatus: RunStatus;
  references: CaseReferences;
}

export const RunCaseIterations: FC<Props> = ({ projectKey, runCase, runStatus, references }) => {
  const { t } = useTranslation("dataRows");
  const formatDuration = useFormatDuration();

  return (
    <ol className={styles.iterations} aria-label={t("iteration.listLabel", { code: runCase.code })}>
      {runCase.iterations.map((iteration) => {
        const number = formatIterationNumber(iteration.iteration);
        const outcome = resolveCaseOutcome(iteration.result, runStatus);
        const durationMs = iteration.result?.durationMs ?? null;
        const headingId = `iteration-${runCase.code}-${iteration.iteration}`;

        return (
          <li key={iteration.iteration} className={styles.iteration} aria-labelledby={headingId}>
            <div className={styles.header}>
              <span className={styles.heading}>
                <DSIcon name="iteration" size={16} />
                <DSTitle order={3} type="section" className={styles.title}>
                  <span id={headingId}>{t("iteration.title", { number })}</span>
                </DSTitle>
              </span>
              <span className={styles.meta}>
                <StatusBadge status={outcome} />
                {durationMs !== null && (
                  <DSText size="sm" color="muted" component="span">
                    {formatDuration(durationMs)}
                  </DSText>
                )}
              </span>
            </div>
            <IterationValues
              parameters={runCase.parameters}
              values={iteration.values}
              references={references}
            />
            {iteration.result !== null && iteration.result.suspectedCause !== null && (
              <SuspectedCause
                cause={iteration.result.suspectedCause}
                reason={iteration.result.causeReason}
              />
            )}
            <RunCaseSteps
              projectKey={projectKey}
              caseCode={runCase.code}
              steps={iteration.steps}
              outcome={outcome}
              runStatus={runStatus}
              references={references}
              values={iteration.values}
              ariaLabel={t("iteration.stepsLabel", { code: runCase.code, number })}
            />
          </li>
        );
      })}
    </ol>
  );
};
