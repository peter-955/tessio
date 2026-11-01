"use client";

import { DSBadge, DSCard, DSTable, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { CRITERION_STATUS_COLORS } from "../../../typing/constants/run.constant";
import type { CriterionImpact } from "../../../typing/types/run.type";
import styles from "./report-criteria.module.scss";

interface Props {
  criterionImpacts: CriterionImpact[];
}

const EMPTY_CODES = "—";

const joinCodes = (codes: string[]): string => {
  return codes.length === 0 ? EMPTY_CODES : codes.join(", ");
};

export const ReportCriteria: FC<Props> = ({ criterionImpacts }) => {
  const { t } = useTranslation("runs");

  return (
    <DSCard title={t("report.criteria")}>
      {criterionImpacts.length === 0 ? (
        <DSText color="muted">{t("report.noCriteria")}</DSText>
      ) : (
        <DSTable label={t("report.criteria")}>
          <caption className={styles.caption}>{t("report.criteria")}</caption>
          <thead>
            <tr>
              <th scope="col">{t("report.criterion")}</th>
              <th scope="col">{t("table.status")}</th>
              <th scope="col">{t("report.runCases")}</th>
              <th scope="col">{t("report.failedCaseCodes")}</th>
            </tr>
          </thead>
          <tbody>
            {criterionImpacts.map((impact) => {
              return (
                <tr key={impact.criterionId}>
                  <td>
                    <div className={styles.criterion}>
                      <span className={styles.code}>{impact.code}</span>
                      <span className={styles.text}>{impact.text}</span>
                    </div>
                  </td>
                  <td>
                    <DSBadge color={CRITERION_STATUS_COLORS[impact.status]} hasDot>
                      {t(`criterionStatus.${impact.status}`)}
                    </DSBadge>
                  </td>
                  <td>{joinCodes(impact.runCaseCodes)}</td>
                  <td>{joinCodes(impact.failedCaseCodes)}</td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      )}
    </DSCard>
  );
};
