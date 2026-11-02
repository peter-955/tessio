"use client";

import { DSBadge, DSTable, DSText } from "@/components/design-system";
import { TestCasePriorityBadge } from "@/modules/test-cases/components/test-case-priority-badge/test-case-priority-badge";
import { TextDiff } from "@/modules/test-cases/components/text-diff/text-diff";
import type {
  DiffToken,
  TextDiffLabels,
} from "@/modules/test-cases/typing/types/version-diff.type";
import classNames from "classnames";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { COMPARE_ROW_KIND_COLORS } from "../../typing/constants/version-comparison.constant";
import type {
  CompareRowKind,
  CompareStepRow,
  VersionComparison,
} from "../../typing/types/version-comparison.type";
import { CompareStepCell } from "../compare-step-cell/compare-step-cell";
import styles from "./compare-table.module.scss";

interface Props {
  comparison: VersionComparison;
  olderHeading: string;
  newerHeading: string;
  label: string;
  isOnlyChanges: boolean;
}

export const CompareTable: FC<Props> = ({
  comparison,
  olderHeading,
  newerHeading,
  label,
  isOnlyChanges,
}) => {
  const { t } = useTranslation("caseReview");
  const diffLabels: TextDiffLabels = { added: t("compare.added"), removed: t("compare.removed") };
  const isShown = (kind: CompareRowKind): boolean => !isOnlyChanges || kind !== "unchanged";
  const fields = comparison.fields.filter((row) => isShown(row.kind));
  const steps = comparison.steps.filter((row) => isShown(row.kind));
  const isPriorityShown = isShown(comparison.priority.kind);
  const dataTable =
    comparison.dataTable !== null && isShown(comparison.dataTable.kind)
      ? comparison.dataTable
      : null;

  const renderKind = (kind: CompareRowKind): ReactNode => {
    if (kind === "unchanged") {
      return null;
    }

    return <DSBadge color={COMPARE_ROW_KIND_COLORS[kind]}>{t(`compare.kind.${kind}`)}</DSBadge>;
  };

  const renderText = (tokens: readonly DiffToken[]): ReactNode => {
    return tokens.length === 0 ? (
      <DSText color="muted">{t("compare.empty")}</DSText>
    ) : (
      <TextDiff tokens={tokens} labels={diffLabels} />
    );
  };

  const describeStep = (row: CompareStepRow): string => {
    const olderOrder = row.left?.order ?? null;
    const newerOrder = row.right?.order ?? null;
    if (olderOrder !== null && newerOrder !== null && olderOrder !== newerOrder) {
      return t("compare.stepMoved", { from: olderOrder, to: newerOrder });
    }

    return t("compare.step", { order: olderOrder ?? newerOrder });
  };

  return (
    <DSTable label={label}>
      <thead>
        <tr>
          <th scope="col">{t("compare.itemColumn")}</th>
          <th scope="col">{olderHeading}</th>
          <th scope="col">{newerHeading}</th>
        </tr>
      </thead>
      <tbody>
        {fields.map((row) => {
          const isChanged = row.kind === "changed";

          return (
            <tr key={row.field} className={styles.row}>
              <th scope="row" className={styles.item}>
                <span className={styles.itemName}>{t(`compare.fields.${row.field}`)}</span>
                {renderKind(row.kind)}
              </th>
              <td className={classNames(styles.cell, isChanged && styles.olderChanged)}>
                {renderText(row.left)}
              </td>
              <td className={classNames(styles.cell, isChanged && styles.newerChanged)}>
                {renderText(row.right)}
              </td>
            </tr>
          );
        })}
        {isPriorityShown && (
          <tr className={styles.row}>
            <th scope="row" className={styles.item}>
              <span className={styles.itemName}>{t("compare.fields.priority")}</span>
              {renderKind(comparison.priority.kind)}
            </th>
            <td className={styles.cell}>
              <TestCasePriorityBadge priority={comparison.priority.left} />
            </td>
            <td className={styles.cell}>
              <TestCasePriorityBadge priority={comparison.priority.right} />
            </td>
          </tr>
        )}
        {dataTable !== null && (
          <tr className={styles.row}>
            <th scope="row" className={styles.item}>
              <span className={styles.itemName}>{t("compare.fields.dataTable")}</span>
              {renderKind(dataTable.kind)}
            </th>
            <td
              className={classNames(
                styles.cell,
                dataTable.kind === "changed" && styles.olderChanged,
              )}
            >
              {renderText(dataTable.left)}
            </td>
            <td
              className={classNames(
                styles.cell,
                dataTable.kind === "changed" && styles.newerChanged,
              )}
            >
              {renderText(dataTable.right)}
            </td>
          </tr>
        )}
        {steps.map((row, index) => {
          return (
            <tr key={index} className={styles.row}>
              <th scope="row" className={styles.item}>
                <span className={styles.itemName}>{describeStep(row)}</span>
                {renderKind(row.kind)}
              </th>
              <td
                className={classNames(styles.cell, {
                  [styles.olderChanged]: row.kind === "changed",
                  [styles.removed]: row.kind === "removed",
                })}
              >
                <CompareStepCell side={row.left} labels={diffLabels} />
              </td>
              <td
                className={classNames(styles.cell, {
                  [styles.newerChanged]: row.kind === "changed",
                  [styles.added]: row.kind === "added",
                })}
              >
                <CompareStepCell side={row.right} labels={diffLabels} />
              </td>
            </tr>
          );
        })}
        {!isOnlyChanges && comparison.steps.length === 0 && (
          <tr className={styles.row}>
            <th scope="row" className={styles.item}>
              <span className={styles.itemName}>{t("compare.stepsLabel")}</span>
            </th>
            <td className={styles.cell} colSpan={2}>
              <DSText color="muted">{t("compare.noSteps")}</DSText>
            </td>
          </tr>
        )}
      </tbody>
    </DSTable>
  );
};
