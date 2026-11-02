"use client";

import { CaseSheet } from "@/components/case-sheet/case-sheet";
import type {
  CaseReferences,
  CaseSecretReveal,
} from "@/components/case-sheet/typing/types/case-sheet.type";
import { DSText, DSTitle } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseDraft } from "../../typing/types/case-draft.type";
import type { ManualRunCase, ResultStatus } from "../../typing/types/manual-run.type";
import type { StepDraft } from "../../typing/types/step-draft.type";
import { CaseResultForm } from "../case-result-form/case-result-form";
import styles from "./case-recorder.module.scss";

interface Props {
  runCase: ManualRunCase;
  draft: CaseDraft;
  references: CaseReferences;
  secretReveal: CaseSecretReveal;
  onStepChange: (order: number, changes: Partial<StepDraft>) => void;
  onStatusOverrideChange: (statusOverride: ResultStatus | null) => void;
  onCauseChange: (changes: Partial<Pick<CaseDraft, "suspectedCause" | "causeReason">>) => void;
  onSave: () => void;
  isSaving: boolean;
  errorMessage: string | null;
}

export const CaseRecorder: FC<Props> = ({
  runCase,
  draft,
  references,
  secretReveal,
  onStepChange,
  onStatusOverrideChange,
  onCauseChange,
  onSave,
  isSaving,
  errorMessage,
}) => {
  const { t } = useTranslation("manualRun");

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
      <CaseResultForm
        steps={runCase.steps}
        draft={draft}
        references={references}
        ariaLabel={t("record.stepsOf", { code: runCase.code })}
        onStepChange={onStepChange}
        onStatusOverrideChange={onStatusOverrideChange}
        onCauseChange={onCauseChange}
        onSave={onSave}
        isSaving={isSaving}
        errorMessage={errorMessage}
      />
    </section>
  );
};
