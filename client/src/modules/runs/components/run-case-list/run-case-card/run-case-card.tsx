"use client";

import {
  DSButton,
  DSCard,
  DSStepTimeline,
  DSText,
  type DSStepTimelineLabels,
  type DSStepTimelineStep,
} from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { useFormatDuration } from "@/shared/hooks/use-format-duration";
import type { RunCase, RunStatus } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import { useId, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { EXPANDED_CASE_STATUSES } from "../../../typing/constants/run.constant";
import { resolveCaseOutcome, resolveStepOutcome } from "../../../utils/run-outcome.util";
import { buildCasePath } from "../../../utils/run-path.util";
import { resolveScreenshotState } from "../../../utils/screenshot-state.util";
import styles from "./run-case-card.module.scss";
import { StepEvidence } from "./step-evidence/step-evidence";
import { StepScreenshot } from "./step-screenshot/step-screenshot";

interface Props {
  projectKey: string;
  runCase: RunCase;
  runStatus: RunStatus;
}

export const RunCaseCard: FC<Props> = ({ projectKey, runCase, runStatus }) => {
  const { t } = useTranslation("runs");
  const formatDuration = useFormatDuration();
  const stepsId = useId();
  const outcome = resolveCaseOutcome(runCase.result, runStatus);
  const isExpandedByDefault = EXPANDED_CASE_STATUSES.includes(outcome);
  const [isExpanded, setIsExpanded] = useState(isExpandedByDefault);
  const [syncedOutcome, setSyncedOutcome] = useState(outcome);

  if (outcome !== syncedOutcome) {
    setSyncedOutcome(outcome);
    if (isExpandedByDefault) {
      setIsExpanded(true);
    }
  }

  const labels: DSStepTimelineLabels = {
    step: (order) => t("step.label", { order }),
    expected: t("step.expected"),
    actualResult: t("step.actualResult"),
    error: t("step.error"),
  };

  const steps = runCase.steps.map((step): DSStepTimelineStep => {
    const status = resolveStepOutcome(step.status, outcome);
    const screenshotState = resolveScreenshotState(
      step.screenshotFileId,
      step.screenshotStatus,
      runStatus,
    );
    const hasMedia = screenshotState !== "none" || step.evidenceFileId !== null;

    return {
      key: String(step.order),
      order: step.order,
      action: step.action,
      expected: step.expected,
      status,
      statusLabel: t(`status.${status}`),
      actualResult: step.actualResult,
      error: step.error,
      media: hasMedia ? (
        <div className={styles.media}>
          {step.screenshotFileId !== null && (
            <StepScreenshot
              projectKey={projectKey}
              fileId={step.screenshotFileId}
              state={screenshotState}
              alt={t("screenshot.alt", { code: runCase.code, order: step.order })}
            />
          )}
          {step.evidenceFileId !== null && (
            <StepEvidence projectKey={projectKey} fileId={step.evidenceFileId} />
          )}
        </div>
      ) : undefined,
    };
  });

  const durationMs = runCase.result?.durationMs ?? null;
  const toggleLabel = isExpanded ? t("case.hideSteps") : t("case.showSteps");

  return (
    <li id={`case-${runCase.code}`} className={styles.item}>
      <DSCard className={styles.card}>
        <div className={styles.header}>
          <div className={styles.identity}>
            <Link href={buildCasePath(projectKey, runCase.code)} className={styles.code}>
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
        {outcome === "not_reported" && (
          <DSText size="sm" color="muted" className={styles.hint}>
            {t("detail.notReportedHint")}
          </DSText>
        )}
        <div id={stepsId} hidden={!isExpanded} className={styles.steps}>
          {isExpanded && (
            <DSStepTimeline
              steps={steps}
              labels={labels}
              ariaLabel={t("case.stepsLabel", { code: runCase.code })}
            />
          )}
        </div>
      </DSCard>
    </li>
  );
};
