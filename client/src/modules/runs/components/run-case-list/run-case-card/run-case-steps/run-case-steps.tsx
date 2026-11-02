"use client";

import { ReferenceText } from "@/components/case-sheet/reference-text/reference-text";
import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import {
  DSStepTimeline,
  type DSStepTimelineLabels,
  type DSStepTimelineStep,
} from "@/components/design-system";
import { StepDiagnosis } from "@/components/step-diagnosis/step-diagnosis";
import type { DataRow } from "@/modules/data-rows/typing/types/data-table.type";
import { fillParameters } from "@/modules/data-rows/utils/parameter-text.util";
import type { RunStatus, StepResult } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ResultOutcome } from "../../../../typing/types/run.type";
import { resolveStepOutcome } from "../../../../utils/run-outcome.util";
import { resolveScreenshotState } from "../../../../utils/screenshot-state.util";
import styles from "../run-case-card.module.scss";
import { StepEvidence } from "../step-evidence/step-evidence";
import { StepScreenshot } from "../step-screenshot/step-screenshot";

interface Props {
  projectKey: string;
  caseCode: string;
  steps: readonly StepResult[];
  outcome: ResultOutcome;
  runStatus: RunStatus;
  references: CaseReferences;
  ariaLabel: string;
  values?: DataRow;
}

export const RunCaseSteps: FC<Props> = ({
  projectKey,
  caseCode,
  steps,
  outcome,
  runStatus,
  references,
  ariaLabel,
  values = {},
}) => {
  const { t } = useTranslation("runs");

  const labels: DSStepTimelineLabels = {
    step: (order) => t("step.label", { order }),
    expected: t("step.expected"),
    actualResult: t("step.actualResult"),
    error: t("step.error"),
  };

  const timelineSteps = steps.map((step): DSStepTimelineStep => {
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
      action: <ReferenceText text={fillParameters(step.action, values)} references={references} />,
      expected:
        step.expected === null ? null : (
          <ReferenceText text={fillParameters(step.expected, values)} references={references} />
        ),
      status,
      statusLabel: t(`status.${status}`),
      actualResult: step.actualResult,
      error: step.error,
      details: step.diagnosis === null ? undefined : <StepDiagnosis diagnosis={step.diagnosis} />,
      media: hasMedia ? (
        <div className={styles.media}>
          {step.screenshotFileId !== null && (
            <StepScreenshot
              projectKey={projectKey}
              fileId={step.screenshotFileId}
              state={screenshotState}
              alt={t("screenshot.alt", { code: caseCode, order: step.order })}
            />
          )}
          {step.evidenceFileId !== null && (
            <StepEvidence projectKey={projectKey} fileId={step.evidenceFileId} />
          )}
        </div>
      ) : undefined,
    };
  });

  return <DSStepTimeline steps={timelineSteps} labels={labels} ariaLabel={ariaLabel} />;
};
