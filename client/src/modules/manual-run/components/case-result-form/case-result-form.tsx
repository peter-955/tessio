"use client";

import { ReferenceText } from "@/components/case-sheet/reference-text/reference-text";
import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import {
  DSAlert,
  DSButton,
  DSStepTimeline,
  DSText,
  type DSStepTimelineStep,
} from "@/components/design-system";
import type { DataRow } from "@/modules/data-rows/typing/types/data-table.type";
import { fillParameters } from "@/modules/data-rows/utils/parameter-text.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { ERROR_RESULT_STATUSES } from "../../typing/constants/result-status.constant";
import type { CaseDraft } from "../../typing/types/case-draft.type";
import type { ManualRunStep, ResultStatus } from "../../typing/types/manual-run.type";
import type { StepDraft } from "../../typing/types/step-draft.type";
import { checkIsCaseDraftUploading, listDraftStatuses } from "../../utils/case-result-request.util";
import { readStepDraft } from "../../utils/step-draft.util";
import { suggestCaseStatus } from "../../utils/suggest-case-status.util";
import { StepRecorder } from "../step-recorder/step-recorder";
import { SuggestedStatusField } from "../suggested-status-field/suggested-status-field";
import { SuspectedCauseField } from "../suspected-cause-field/suspected-cause-field";
import styles from "./case-result-form.module.scss";

interface Props {
  steps: readonly ManualRunStep[];
  draft: CaseDraft;
  references: CaseReferences;
  ariaLabel: string;
  onStepChange: (order: number, changes: Partial<StepDraft>) => void;
  onStatusOverrideChange: (statusOverride: ResultStatus | null) => void;
  onCauseChange: (changes: Partial<Pick<CaseDraft, "suspectedCause" | "causeReason">>) => void;
  onSave: () => void;
  isSaving: boolean;
  errorMessage: string | null;
  values?: DataRow;
  saveLabel?: string;
}

export const CaseResultForm: FC<Props> = ({
  steps,
  draft,
  references,
  ariaLabel,
  onStepChange,
  onStatusOverrideChange,
  onCauseChange,
  onSave,
  isSaving,
  errorMessage,
  values = {},
  saveLabel,
}) => {
  const { t } = useTranslation("manualRun");
  const isUploading = checkIsCaseDraftUploading(draft);
  const statuses = listDraftStatuses(draft, steps);
  const caseStatus = draft.statusOverride ?? suggestCaseStatus(statuses);
  const timelineSteps = steps.map((step): DSStepTimelineStep => {
    const stepDraft = readStepDraft(draft, step.order);

    return {
      key: String(step.order),
      order: step.order,
      action: <ReferenceText text={fillParameters(step.action, values)} references={references} />,
      expected:
        step.expected === null || step.expected === "" ? null : (
          <ReferenceText text={fillParameters(step.expected, values)} references={references} />
        ),
      status: stepDraft.status ?? undefined,
      statusLabel: stepDraft.status === null ? undefined : t(`status.${stepDraft.status}`),
      details: (
        <StepRecorder
          order={step.order}
          stepDraft={stepDraft}
          onChange={(changes) => {
            onStepChange(step.order, changes);
          }}
        />
      ),
    };
  });

  return (
    <div className={styles.form}>
      {steps.length === 0 ? (
        <DSText color="muted">{t("record.noSteps")}</DSText>
      ) : (
        <DSStepTimeline
          steps={timelineSteps}
          labels={{
            step: (order) => t("record.step", { order }),
            expected: t("record.expected"),
          }}
          ariaLabel={ariaLabel}
        />
      )}
      <SuggestedStatusField
        statuses={statuses}
        statusOverride={draft.statusOverride}
        onChange={onStatusOverrideChange}
        isDisabled={isSaving}
      />
      {ERROR_RESULT_STATUSES.includes(caseStatus) && (
        <SuspectedCauseField
          cause={draft.suspectedCause}
          reason={draft.causeReason}
          onChange={onCauseChange}
          isDisabled={isSaving}
        />
      )}
      {errorMessage !== null && <DSAlert color="danger">{errorMessage}</DSAlert>}
      <div className={styles.actions}>
        <DSButton
          type="primary"
          icon="check"
          isDisabled={isUploading}
          isLoading={isSaving}
          onClick={onSave}
        >
          {saveLabel ?? t("record.save")}
        </DSButton>
      </div>
    </div>
  );
};
