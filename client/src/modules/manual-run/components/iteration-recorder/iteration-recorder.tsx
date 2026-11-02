"use client";

import { CaseSheet } from "@/components/case-sheet/case-sheet";
import type {
  CaseReferences,
  CaseSecretReveal,
} from "@/components/case-sheet/typing/types/case-sheet.type";
import { DSButton, DSIcon, DSText, DSTitle } from "@/components/design-system";
import { SuspectedCause } from "@/components/suspected-cause/suspected-cause";
import { IterationValues } from "@/modules/data-rows/components/iteration-values/iteration-values";
import { formatIterationNumber } from "@/modules/data-rows/utils/parameter-text.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseDraft } from "../../typing/types/case-draft.type";
import type { ManualRunCase, ResultStatus } from "../../typing/types/manual-run.type";
import type { StepDraft } from "../../typing/types/step-draft.type";
import { countRecordedIterations } from "../../utils/run-case.util";
import { CaseResultForm } from "../case-result-form/case-result-form";
import { RecordedSteps } from "../recorded-steps/recorded-steps";
import { ResultStatusBadge } from "../result-status-badge/result-status-badge";
import styles from "./iteration-recorder.module.scss";

interface Props {
  runCase: ManualRunCase;
  activeIteration: number;
  readDraft: (iteration: number) => CaseDraft;
  references: CaseReferences;
  secretReveal: CaseSecretReveal;
  canRecord: boolean;
  onSelectIteration: (iteration: number) => void;
  onStepChange: (iteration: number, order: number, changes: Partial<StepDraft>) => void;
  onStatusOverrideChange: (iteration: number, statusOverride: ResultStatus | null) => void;
  onCauseChange: (
    iteration: number,
    changes: Partial<Pick<CaseDraft, "suspectedCause" | "causeReason">>,
  ) => void;
  onSave: (iteration: number) => void;
  isSaving: boolean;
  errorMessage: string | null;
}

export const IterationRecorder: FC<Props> = ({
  runCase,
  activeIteration,
  readDraft,
  references,
  secretReveal,
  canRecord,
  onSelectIteration,
  onStepChange,
  onStatusOverrideChange,
  onCauseChange,
  onSave,
  isSaving,
  errorMessage,
}) => {
  const { t } = useTranslation("dataRows");
  const { t: tManualRun } = useTranslation("manualRun");
  const caseLabel = `${runCase.code} · ${runCase.title}`;

  return (
    <section className={styles.recorder} aria-label={caseLabel}>
      <div className={styles.header}>
        <DSTitle order={2} type="section" className={styles.title}>
          {caseLabel}
        </DSTitle>
        <DSText size="sm" color="muted" component="span">
          {t("iteration.summary", {
            count: runCase.iterations.length,
            recorded: countRecordedIterations(runCase),
          })}
        </DSText>
      </div>
      <CaseSheet
        criteria={runCase.criteria}
        businessValue={runCase.businessValue}
        preconditions={runCase.preconditions}
        steps={runCase.steps}
        references={references}
        isStepListShown={false}
        headingOrder={3}
        secretReveal={secretReveal}
      />
      <DSText size="sm" color="muted">
        {t("iteration.recordHint")}
      </DSText>
      <ol
        className={styles.iterations}
        aria-label={t("iteration.listLabel", { code: runCase.code })}
      >
        {runCase.iterations.map((iteration) => {
          const number = formatIterationNumber(iteration.iteration);
          const isActive = iteration.iteration === activeIteration;
          const isRecorded = iteration.result !== null;
          const headingId = `record-iteration-${runCase.testCaseId}-${iteration.iteration}`;
          const stepsLabel = t("iteration.stepsLabel", { code: runCase.code, number });

          return (
            <li
              key={iteration.iteration}
              className={styles.iteration}
              aria-labelledby={headingId}
              aria-current={isActive ? "step" : undefined}
            >
              <div className={styles.iterationHeader}>
                <span className={styles.heading}>
                  <DSIcon name="iteration" size={16} />
                  <DSTitle order={3} type="section">
                    <span id={headingId}>{t("iteration.title", { number })}</span>
                  </DSTitle>
                </span>
                {iteration.result === null ? (
                  <DSText size="sm" color="muted" component="span">
                    {tManualRun("record.notRecorded")}
                  </DSText>
                ) : (
                  <ResultStatusBadge status={iteration.result.status} />
                )}
              </div>
              <IterationValues
                parameters={runCase.parameters}
                values={iteration.values}
                references={references}
              />
              {!isActive && (
                <div className={styles.open}>
                  <DSButton
                    type={!isRecorded && canRecord ? "outline" : "ghost"}
                    size="sm"
                    icon={!isRecorded && canRecord ? "edit" : "eye"}
                    onClick={() => {
                      onSelectIteration(iteration.iteration);
                    }}
                  >
                    {!isRecorded && canRecord
                      ? t("iteration.record", { number })
                      : t("iteration.showSteps", { number })}
                  </DSButton>
                </div>
              )}
              {isActive &&
                iteration.result !== null &&
                iteration.result.suspectedCause !== null && (
                  <SuspectedCause
                    cause={iteration.result.suspectedCause}
                    reason={iteration.result.causeReason}
                  />
                )}
              {isActive &&
                (!isRecorded && canRecord ? (
                  <CaseResultForm
                    key={iteration.iteration}
                    steps={iteration.steps}
                    draft={readDraft(iteration.iteration)}
                    references={references}
                    values={iteration.values}
                    ariaLabel={stepsLabel}
                    onStepChange={(order, changes) => {
                      onStepChange(iteration.iteration, order, changes);
                    }}
                    onStatusOverrideChange={(statusOverride) => {
                      onStatusOverrideChange(iteration.iteration, statusOverride);
                    }}
                    onCauseChange={(changes) => {
                      onCauseChange(iteration.iteration, changes);
                    }}
                    onSave={() => {
                      onSave(iteration.iteration);
                    }}
                    isSaving={isSaving}
                    errorMessage={errorMessage}
                    saveLabel={t("iteration.save", { number })}
                  />
                ) : (
                  <RecordedSteps
                    steps={iteration.steps}
                    references={references}
                    values={iteration.values}
                    ariaLabel={stepsLabel}
                  />
                ))}
            </li>
          );
        })}
      </ol>
    </section>
  );
};
