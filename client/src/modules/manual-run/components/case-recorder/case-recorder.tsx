"use client";

import { DSAlert, DSButton, DSText, DSTitle } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseDraft } from "../../typing/types/case-draft.type";
import type { ManualRunCase, ResultStatus } from "../../typing/types/manual-run.type";
import type { StepDraft } from "../../typing/types/step-draft.type";
import { checkIsCaseDraftUploading, listDraftStatuses } from "../../utils/case-result-request.util";
import { readStepDraft } from "../../utils/step-draft.util";
import { StepRecorder } from "../step-recorder/step-recorder";
import { SuggestedStatusField } from "../suggested-status-field/suggested-status-field";
import styles from "./case-recorder.module.scss";

interface Props {
  runCase: ManualRunCase;
  draft: CaseDraft;
  onStepChange: (order: number, changes: Partial<StepDraft>) => void;
  onStatusOverrideChange: (statusOverride: ResultStatus | null) => void;
  onSave: () => void;
  isSaving: boolean;
  errorMessage: string | null;
}

export const CaseRecorder: FC<Props> = ({
  runCase,
  draft,
  onStepChange,
  onStatusOverrideChange,
  onSave,
  isSaving,
  errorMessage,
}) => {
  const { t } = useTranslation("manualRun");
  const isUploading = checkIsCaseDraftUploading(draft);

  return (
    <section className={styles.recorder} aria-label={`${runCase.code} · ${runCase.title}`}>
      <div className={styles.header}>
        <DSTitle order={2} type="section" className={styles.title}>
          {`${runCase.code} · ${runCase.title}`}
        </DSTitle>
        <DSText size="sm" color="muted" component="span">
          {t("record.notRecorded")}
        </DSText>
      </div>
      {runCase.steps.length === 0 ? (
        <DSText color="muted">{t("record.noSteps")}</DSText>
      ) : (
        <ol className={styles.steps}>
          {runCase.steps.map((step) => {
            return (
              <StepRecorder
                key={step.order}
                step={step}
                stepDraft={readStepDraft(draft, step.order)}
                onChange={(changes) => {
                  onStepChange(step.order, changes);
                }}
              />
            );
          })}
        </ol>
      )}
      <SuggestedStatusField
        statuses={listDraftStatuses(draft, runCase.steps)}
        statusOverride={draft.statusOverride}
        onChange={onStatusOverrideChange}
        isDisabled={isSaving}
      />
      {errorMessage !== null && <DSAlert color="danger">{errorMessage}</DSAlert>}
      <div className={styles.actions}>
        <DSButton
          type="primary"
          icon="check"
          isDisabled={isUploading}
          isLoading={isSaving}
          onClick={onSave}
        >
          {t("record.save")}
        </DSButton>
      </div>
    </section>
  );
};
