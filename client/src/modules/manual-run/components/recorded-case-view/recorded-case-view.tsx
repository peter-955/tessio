"use client";

import { DSIcon, DSText, DSTitle } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ManualRunCase } from "../../typing/types/manual-run.type";
import { ResultStatusBadge } from "../result-status-badge/result-status-badge";
import styles from "./recorded-case-view.module.scss";

interface Props {
  runCase: ManualRunCase;
}

export const RecordedCaseView: FC<Props> = ({ runCase }) => {
  const { t } = useTranslation("manualRun");

  return (
    <section className={styles.view} aria-label={`${runCase.code} · ${runCase.title}`}>
      <div className={styles.header}>
        <DSTitle order={2} type="section" className={styles.title}>
          {`${runCase.code} · ${runCase.title}`}
        </DSTitle>
        {runCase.result === null ? (
          <DSText size="sm" color="muted" component="span">
            {t("record.notRecorded")}
          </DSText>
        ) : (
          <ResultStatusBadge status={runCase.result.status} />
        )}
      </div>
      {runCase.steps.length === 0 ? (
        <DSText color="muted">{t("record.noSteps")}</DSText>
      ) : (
        <ol className={styles.steps}>
          {runCase.steps.map((step) => {
            return (
              <li key={step.order} className={styles.step}>
                <div className={styles.stepHeader}>
                  <DSText size="sm" weight="medium" component="span">
                    {t("record.step", { order: step.order })}
                  </DSText>
                  {step.status === null ? (
                    <DSText size="sm" color="muted" component="span">
                      {t("record.notReported")}
                    </DSText>
                  ) : (
                    <ResultStatusBadge status={step.status} />
                  )}
                </div>
                <DSText className={styles.text}>{step.action}</DSText>
                {step.expected !== null && (
                  <DSText size="sm" color="muted" className={styles.text}>
                    {t("record.expectedValue", { text: step.expected })}
                  </DSText>
                )}
                {step.actualResult !== null && step.actualResult !== "" && (
                  <DSText size="sm" className={styles.text}>
                    {t("record.actualResult")}: {step.actualResult}
                  </DSText>
                )}
                {step.error !== null && step.error !== "" && (
                  <DSText size="sm" color="danger" className={styles.text}>
                    {t("record.error")}: {step.error}
                  </DSText>
                )}
                {step.evidenceFileId !== null && (
                  <span className={styles.evidence}>
                    <DSIcon name="file" size={16} />
                    <DSText size="sm" component="span">
                      {t("record.evidenceAttached")}
                    </DSText>
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
};
