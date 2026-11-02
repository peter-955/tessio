"use client";

import { ReferenceText } from "@/components/case-sheet/reference-text/reference-text";
import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { DataRow } from "../../typing/types/data-table.type";
import styles from "./iteration-values.module.scss";

interface Props {
  parameters: readonly string[];
  values: DataRow;
  references?: CaseReferences;
}

export const IterationValues: FC<Props> = ({ parameters, values, references }) => {
  const { t } = useTranslation("dataRows");
  const names = parameters.length > 0 ? parameters : Object.keys(values);

  return (
    <dl className={styles.values} aria-label={t("iteration.values")}>
      {names.map((name) => {
        const value = values[name] ?? "";

        return (
          <div key={name} className={styles.value}>
            <dt className={styles.name}>{name}</dt>
            <dd className={styles.text}>
              {value === "" ? (
                <span className={styles.empty}>{t("iteration.emptyValue")}</span>
              ) : references === undefined ? (
                value
              ) : (
                <ReferenceText text={value} references={references} />
              )}
            </dd>
          </div>
        );
      })}
    </dl>
  );
};
