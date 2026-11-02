"use client";

import { CaseSheet } from "@/components/case-sheet/case-sheet";
import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import { listReferencedKeys } from "@/components/case-sheet/utils/split-references.util";
import { DSButton, DSCard, DSText } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { SuspectedCause } from "@/components/suspected-cause/suspected-cause";
import { useFormatDuration } from "@/shared/hooks/use-format-duration";
import type { RunCase, RunStatus } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import { useId, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { EXPANDED_CASE_STATUSES } from "../../../typing/constants/run.constant";
import { resolveCaseOutcome } from "../../../utils/run-outcome.util";
import { buildCaseVersionPath } from "../../../utils/run-path.util";
import styles from "./run-case-card.module.scss";
import { RunCaseIterations } from "./run-case-iterations/run-case-iterations";
import { RunCaseSteps } from "./run-case-steps/run-case-steps";

interface Props {
  projectKey: string;
  runCase: RunCase;
  runStatus: RunStatus;
  references: CaseReferences;
}

export const RunCaseCard: FC<Props> = ({ projectKey, runCase, runStatus, references }) => {
  const { t } = useTranslation("runs");
  const { t: tDataRows } = useTranslation("dataRows");
  const formatDuration = useFormatDuration();
  const isDataDriven = runCase.iterations.length > 0;
  const stepsId = useId();
  const outcome = resolveCaseOutcome(runCase.result, runStatus);
  const isExpandedByDefault = EXPANDED_CASE_STATUSES.includes(outcome);
  const [isExpanded, setIsExpanded] = useState(isExpandedByDefault);
  const [syncedOutcome, setSyncedOutcome] = useState(outcome);
  const [isDetailShown, setIsDetailShown] = useState(false);
  const detailId = useId();
  const hasDetails =
    runCase.criteria.length > 0 ||
    Boolean(runCase.businessValue) ||
    Boolean(runCase.preconditions) ||
    listReferencedKeys([], runCase.steps).dataKeys.length > 0;

  if (outcome !== syncedOutcome) {
    setSyncedOutcome(outcome);
    if (isExpandedByDefault) {
      setIsExpanded(true);
    }
  }

  const durationMs = runCase.result?.durationMs ?? null;
  const toggleLabel = isExpanded ? t("case.hideSteps") : t("case.showSteps");

  return (
    <li id={`case-${runCase.code}`} className={styles.item}>
      <DSCard className={styles.card}>
        <div className={styles.header}>
          <div className={styles.identity}>
            <Link
              href={buildCaseVersionPath(projectKey, runCase.code, runCase.versionNumber)}
              className={styles.code}
            >
              {runCase.code}
            </Link>
            <DSText weight="medium" component="span" className={styles.title}>
              {runCase.title}
            </DSText>
            <DSText size="xs" color="muted" component="span">
              {t("case.version", { number: runCase.versionNumber })}
            </DSText>
          </div>
          <div className={styles.meta}>
            <StatusBadge status={outcome} />
            {durationMs !== null && (
              <DSText size="sm" color="muted" component="span">
                {formatDuration(durationMs)}
              </DSText>
            )}
            {hasDetails && (
              <DSButton
                type="ghost"
                icon="infoCircle"
                ariaExpanded={isDetailShown}
                ariaControls={detailId}
                onClick={() => {
                  setIsDetailShown(!isDetailShown);
                }}
              >
                {isDetailShown ? t("case.hideDetails") : t("case.showDetails")}
              </DSButton>
            )}
            {isDataDriven && (
              <DSText size="sm" color="muted" component="span">
                {tDataRows("iteration.summary", {
                  count: runCase.iterations.length,
                  recorded: runCase.iterations.filter((iteration) => iteration.result !== null)
                    .length,
                })}
              </DSText>
            )}
            {runCase.steps.length > 0 && (
              <DSButton
                type="ghost"
                icon={isExpanded ? "eyeOff" : "eye"}
                ariaExpanded={isExpanded}
                ariaControls={stepsId}
                onClick={() => {
                  setIsExpanded(!isExpanded);
                }}
              >
                {toggleLabel}
              </DSButton>
            )}
          </div>
        </div>
        {runCase.result !== null && runCase.result.suspectedCause !== null && (
          <div className={styles.cause}>
            <SuspectedCause
              cause={runCase.result.suspectedCause}
              reason={runCase.result.causeReason}
            />
          </div>
        )}
        {outcome === "not_reported" && (
          <DSText size="sm" color="muted" className={styles.hint}>
            {t("detail.notReportedHint")}
          </DSText>
        )}
        <div id={detailId} hidden={!isDetailShown} className={styles.detail}>
          {isDetailShown && (
            <CaseSheet
              criteria={runCase.criteria}
              businessValue={runCase.businessValue}
              preconditions={runCase.preconditions}
              steps={runCase.steps}
              references={references}
              isStepListShown={false}
              headingOrder={3}
            />
          )}
        </div>
        <div id={stepsId} hidden={!isExpanded} className={styles.steps}>
          {isExpanded &&
            (isDataDriven ? (
              <RunCaseIterations
                projectKey={projectKey}
                runCase={runCase}
                runStatus={runStatus}
                references={references}
              />
            ) : (
              <RunCaseSteps
                projectKey={projectKey}
                caseCode={runCase.code}
                steps={runCase.steps}
                outcome={outcome}
                runStatus={runStatus}
                references={references}
                ariaLabel={t("case.stepsLabel", { code: runCase.code })}
              />
            ))}
        </div>
      </DSCard>
    </li>
  );
};
