"use client";

import { DSText } from "@/components/design-system";
import type { StepDiagnosis as StepDiagnosisValue } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./step-diagnosis.module.scss";

interface Props {
  diagnosis: StepDiagnosisValue;
}

export const StepDiagnosis: FC<Props> = ({ diagnosis }) => {
  const { t } = useTranslation("diagnosis");

  return (
    <section className={styles.diagnosis} aria-label={t("whyItFailed")}>
      <DSText size="sm" weight="medium" component="span">
        {t("whyItFailed")}
      </DSText>
      {diagnosis.pageUrl !== null && (
        <div className={styles.field}>
          <span className={styles.label}>{t("page")}</span>
          <code className={styles.code}>{diagnosis.pageUrl}</code>
        </div>
      )}
      {diagnosis.failedRequests.length > 0 && (
        <div className={styles.field}>
          <span className={styles.label}>{t("failedRequests")}</span>
          <ul className={styles.list}>
            {diagnosis.failedRequests.map((failedRequest, index) => {
              return (
                <li key={index} className={styles.item}>
                  <code className={styles.code}>
                    {`${failedRequest.method} ${failedRequest.path} → ${failedRequest.status}`}
                  </code>
                  {failedRequest.excerpt !== null && (
                    <code className={styles.excerpt}>{failedRequest.excerpt}</code>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
      {diagnosis.consoleErrors.length > 0 && (
        <div className={styles.field}>
          <span className={styles.label}>{t("consoleErrors")}</span>
          <ul className={styles.list}>
            {diagnosis.consoleErrors.map((consoleError, index) => {
              return (
                <li key={index} className={styles.item}>
                  <code className={styles.code}>{consoleError}</code>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </section>
  );
};
