import Link from "next/link";
import type { FC } from "react";
import { DSBadge } from "../badge/badge";
import { DSTable } from "../table/table";
import {
  DS_TRACEABILITY_CRITERION_COLORS,
  DS_TRACEABILITY_RESULT_COLORS,
} from "./traceability-matrix.constant";
import styles from "./traceability-matrix.module.scss";
import type {
  DSTraceabilityCase,
  DSTraceabilityCriterion,
  DSTraceabilityMatrixLabels,
} from "./traceability-matrix.type";

interface Props {
  criteria: readonly DSTraceabilityCriterion[];
  cases: readonly DSTraceabilityCase[];
  labels: DSTraceabilityMatrixLabels;
}

export const DSTraceabilityMatrix: FC<Props> = ({ criteria, cases, labels }) => {
  return (
    <DSTable label={labels.caption}>
      <caption className={styles.visuallyHidden}>{labels.caption}</caption>
      <thead>
        <tr>
          <th scope="col" className={styles.criterionHeader}>
            {labels.criterion}
          </th>
          <th scope="col">{labels.status}</th>
          {cases.map((traceabilityCase) => {
            return (
              <th key={traceabilityCase.id} scope="col" className={styles.caseHeader}>
                <span className={styles.caseHeading}>
                  <Link
                    href={traceabilityCase.href}
                    title={traceabilityCase.title}
                    className={styles.caseCode}
                  >
                    {traceabilityCase.code}
                  </Link>
                  <span className={styles.caseTitle}>{traceabilityCase.title}</span>
                  {traceabilityCase.markers.length > 0 && (
                    <span className={styles.markers}>
                      {traceabilityCase.markers.map((marker) => {
                        return (
                          <DSBadge key={marker} color="gray">
                            {marker}
                          </DSBadge>
                        );
                      })}
                    </span>
                  )}
                </span>
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {criteria.map((criterion) => {
          const isRemoved = criterion.removedLabel !== null;
          const linkedCaseIds = new Set(criterion.linkedCaseIds);

          return (
            <tr key={criterion.id} className={isRemoved ? styles.removed : undefined}>
              <th scope="row" className={styles.criterionCell}>
                <span className={styles.criterion}>
                  <DSBadge color="tessio">{criterion.code}</DSBadge>
                  {isRemoved ? (
                    <s className={styles.criterionText}>{criterion.text}</s>
                  ) : (
                    <span className={styles.criterionText}>{criterion.text}</span>
                  )}
                  {criterion.removedLabel !== null && (
                    <DSBadge color="gray">{criterion.removedLabel}</DSBadge>
                  )}
                </span>
              </th>
              <td>
                <DSBadge color={DS_TRACEABILITY_CRITERION_COLORS[criterion.status]} hasDot>
                  {labels.criterionStatuses[criterion.status]}
                </DSBadge>
              </td>
              {cases.map((traceabilityCase) => {
                if (!linkedCaseIds.has(traceabilityCase.id)) {
                  return (
                    <td key={traceabilityCase.id} className={styles.resultCell}>
                      <span aria-hidden="true" className={styles.notLinked}>
                        ·
                      </span>
                      <span className={styles.visuallyHidden}>{labels.notLinked}</span>
                    </td>
                  );
                }

                return (
                  <td key={traceabilityCase.id} className={styles.resultCell}>
                    <DSBadge color={DS_TRACEABILITY_RESULT_COLORS[traceabilityCase.resultStatus]}>
                      {labels.resultStatuses[traceabilityCase.resultStatus]}
                    </DSBadge>
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
