"use client";

import { DSCopyButton } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ReferenceChip } from "../reference-text/reference-chip/reference-chip";
import { SecretRevealAction } from "../secret-reveal-action/secret-reveal-action";
import type { CaseReferences, CaseSecretReveal } from "../typing/types/case-sheet.type";
import styles from "./case-data-table.module.scss";

interface Props {
  dataKeys: readonly string[];
  references: CaseReferences;
  secretReveal?: CaseSecretReveal;
}

export const CaseDataTable: FC<Props> = ({ dataKeys, references, secretReveal }) => {
  const { t } = useTranslation("caseSheet");

  const renderActions = (dataKey: string): ReactNode => {
    const dataValue = references.dataByKey.get(dataKey);
    if (dataValue === undefined) {
      return null;
    }

    if (dataValue.kind !== "secret") {
      return dataValue.value === null ? null : <DSCopyButton value={dataValue.value} />;
    }

    const revealedValue = references.revealedValues[dataKey];

    return (
      <>
        {revealedValue !== undefined && <DSCopyButton value={revealedValue} />}
        {secretReveal !== undefined && (
          <SecretRevealAction
            dataKey={dataKey}
            isRevealed={revealedValue !== undefined}
            secretReveal={secretReveal}
          />
        )}
      </>
    );
  };

  return (
    <dl className={styles.list} aria-label={t("testData")}>
      {dataKeys.map((dataKey) => {
        return (
          <div key={dataKey} className={styles.row}>
            <dt className={styles.key}>{dataKey}</dt>
            <dd className={styles.value}>
              <ReferenceChip kind="data" referenceKey={dataKey} references={references} />
              <span className={styles.actions}>{renderActions(dataKey)}</span>
            </dd>
          </div>
        );
      })}
    </dl>
  );
};
