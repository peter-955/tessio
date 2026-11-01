"use client";

import {
  DSSegmentedControl,
  DSText,
  DSTextarea,
  type DSSegmentedOption,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MAX_RESULT_TEXT_LENGTH } from "../../typing/constants/manual-run.constant";
import {
  ERROR_RESULT_STATUSES,
  NOT_REPORTED_CHOICE,
  RESULT_STATUS_ORDER,
} from "../../typing/constants/result-status.constant";
import type { ManualRunStep } from "../../typing/types/manual-run.type";
import type { StepDraft } from "../../typing/types/step-draft.type";
import type { StepStatusChoice } from "../../typing/types/step-status-choice.type";
import { StepEvidenceField } from "../step-evidence-field/step-evidence-field";
import styles from "./step-recorder.module.scss";

interface Props {
  step: ManualRunStep;
  stepDraft: StepDraft;
  onChange: (changes: Partial<StepDraft>) => void;
}

export const StepRecorder: FC<Props> = ({ step, stepDraft, onChange }) => {
  const { t } = useTranslation("manualRun");
  const statusOptions: DSSegmentedOption<StepStatusChoice>[] = [
    { value: NOT_REPORTED_CHOICE, label: t("record.notReported") },
    ...RESULT_STATUS_ORDER.map((status): DSSegmentedOption<StepStatusChoice> => {
      return { value: status, label: t(`status.${status}`) };
    }),
  ];
  const isErrorShown =
    stepDraft.status !== null && ERROR_RESULT_STATUSES.includes(stepDraft.status);

  const handleStatusChange = (choice: StepStatusChoice): void => {
    onChange({ status: choice === NOT_REPORTED_CHOICE ? null : choice });
  };

  return (
    <li className={styles.step}>
      <div className={styles.instructions}>
        <DSText size="sm" weight="medium" component="span">
          {t("record.step", { order: step.order })}
        </DSText>
        <DSText className={styles.text}>{step.action}</DSText>
        {step.expected !== null && (
          <DSText size="sm" color="muted" className={styles.text}>
            {t("record.expectedValue", { text: step.expected })}
          </DSText>
        )}
      </div>
      <div className={styles.status}>
        <DSSegmentedControl<StepStatusChoice>
          value={stepDraft.status ?? NOT_REPORTED_CHOICE}
          options={statusOptions}
          onChange={handleStatusChange}
          ariaLabel={t("record.stepStatus", { order: step.order })}
          size="xs"
        />
      </div>
      <DSTextarea
        label={t("record.actualResult")}
        value={stepDraft.actualResult}
        onChange={(actualResult) => {
          onChange({ actualResult });
        }}
        maxLength={MAX_RESULT_TEXT_LENGTH}
        minRows={2}
      />
      {isErrorShown && (
        <DSTextarea
          label={t("record.error")}
          value={stepDraft.error}
          onChange={(error) => {
            onChange({ error });
          }}
          maxLength={MAX_RESULT_TEXT_LENGTH}
          minRows={2}
        />
      )}
      <StepEvidenceField stepDraft={stepDraft} onChange={onChange} />
    </li>
  );
};
