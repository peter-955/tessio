"use client";

import { DSText } from "@/components/design-system";
import { TextDiff } from "@/modules/test-cases/components/text-diff/text-diff";
import type {
  DiffToken,
  TextDiffLabels,
} from "@/modules/test-cases/typing/types/version-diff.type";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type { CompareStepSide } from "../../typing/types/version-comparison.type";
import styles from "./compare-step-cell.module.scss";

interface Props {
  side: CompareStepSide | null;
  labels: TextDiffLabels;
}

export const CompareStepCell: FC<Props> = ({ side, labels }) => {
  const { t } = useTranslation("caseReview");

  if (side === null) {
    return <DSText color="muted">{t("compare.noStep")}</DSText>;
  }

  const renderTokens = (tokens: readonly DiffToken[]): ReactNode => {
    return tokens.length === 0 ? (
      <DSText color="muted">{t("compare.empty")}</DSText>
    ) : (
      <TextDiff tokens={tokens} labels={labels} />
    );
  };

  return (
    <div className={styles.step}>
      <div className={styles.part}>
        <span className={styles.label}>{t("compare.action")}</span>
        {renderTokens(side.action)}
      </div>
      <div className={styles.part}>
        <span className={styles.label}>{t("compare.expected")}</span>
        {renderTokens(side.expected)}
      </div>
    </div>
  );
};
