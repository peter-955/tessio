"use client";

import { DSSelect, DSText, type DSSelectOption } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import {
  RESULT_STATUS_ORDER,
  USE_SUGGESTED_CHOICE,
} from "../../typing/constants/result-status.constant";
import type { CaseResultChoice } from "../../typing/types/case-result-choice.type";
import type { ResultStatus } from "../../typing/types/manual-run.type";
import { suggestCaseStatus } from "../../utils/suggest-case-status.util";
import styles from "./suggested-status-field.module.scss";

interface Props {
  statuses: readonly (ResultStatus | null)[];
  statusOverride: ResultStatus | null;
  onChange: (statusOverride: ResultStatus | null) => void;
  isDisabled?: boolean;
}

export const SuggestedStatusField: FC<Props> = ({
  statuses,
  statusOverride,
  onChange,
  isDisabled = false,
}) => {
  const { t } = useTranslation("manualRun");
  const suggestedLabel = t(`status.${suggestCaseStatus(statuses)}`);
  const unmarkedCount = statuses.filter((status) => status === null).length;
  const options: DSSelectOption<CaseResultChoice>[] = [
    { value: USE_SUGGESTED_CHOICE, label: t("record.useSuggested", { status: suggestedLabel }) },
    ...RESULT_STATUS_ORDER.map((status): DSSelectOption<CaseResultChoice> => {
      return { value: status, label: t(`status.${status}`) };
    }),
  ];

  const handleChange = (choice: CaseResultChoice | null): void => {
    onChange(choice === null || choice === USE_SUGGESTED_CHOICE ? null : choice);
  };

  return (
    <div className={styles.field}>
      <div role="status">
        <DSText weight="medium">{t("record.suggested", { status: suggestedLabel })}</DSText>
        {unmarkedCount > 0 && (
          <DSText size="sm" color="muted">
            {t("record.unmarkedSteps", { count: unmarkedCount })}
          </DSText>
        )}
      </div>
      <DSSelect<CaseResultChoice>
        label={t("record.caseResult")}
        value={statusOverride ?? USE_SUGGESTED_CHOICE}
        options={options}
        onChange={handleChange}
        isDisabled={isDisabled}
      />
      <DSText size="sm" color="muted">
        {t("record.hint")}
      </DSText>
    </div>
  );
};
