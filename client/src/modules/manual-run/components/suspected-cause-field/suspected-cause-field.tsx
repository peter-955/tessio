"use client";

import { DSSelect, DSTextarea, type DSSelectOption } from "@/components/design-system";
import { SUSPECTED_CAUSES } from "@/shared/typing/constants/suspected-cause.constant";
import type { SuspectedCause } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MAX_CAUSE_REASON_LENGTH } from "../../typing/constants/manual-run.constant";
import type { CaseDraft } from "../../typing/types/case-draft.type";
import styles from "./suspected-cause-field.module.scss";

interface Props {
  cause: SuspectedCause | null;
  reason: string;
  onChange: (changes: Partial<Pick<CaseDraft, "suspectedCause" | "causeReason">>) => void;
  isDisabled: boolean;
}

export const SuspectedCauseField: FC<Props> = ({ cause, reason, onChange, isDisabled }) => {
  const { t } = useTranslation("manualRun");
  const { t: translateDiagnosis } = useTranslation("diagnosis");
  const options = SUSPECTED_CAUSES.map((value): DSSelectOption<SuspectedCause> => {
    return { value, label: translateDiagnosis(`cause.${value}`) };
  });

  return (
    <div className={styles.field}>
      <DSSelect<SuspectedCause>
        label={translateDiagnosis("suspectedCause")}
        placeholder={t("record.causePlaceholder")}
        value={cause}
        options={options}
        onChange={(suspectedCause) => {
          onChange({ suspectedCause });
        }}
        isClearable
        isDisabled={isDisabled}
      />
      {cause !== null && (
        <DSTextarea
          label={t("record.causeReason")}
          value={reason}
          onChange={(causeReason) => {
            onChange({ causeReason });
          }}
          maxLength={MAX_CAUSE_REASON_LENGTH}
          minRows={1}
          isAutosize
          isDisabled={isDisabled}
        />
      )}
    </div>
  );
};
