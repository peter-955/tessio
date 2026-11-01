"use client";

import { DSButtonLink, DSCard, DSCode, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useCallback, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetFailureRun } from "../../hooks/queries/use-get-failure-run";
import type { FailureDetail, FailureRun } from "../../typing/types/failure.type";
import { findRunStep } from "../../utils/failed-step.util";
import { buildFailureRunPath } from "../../utils/failure-path.util";
import { FailureScreenshot } from "../failure-screenshot/failure-screenshot";
import styles from "./failed-step-card.module.scss";

interface Props {
  failure: FailureDetail;
}

export const FailedStepCard: FC<Props> = ({ failure }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const { failedStep } = failure;
  const stepOrder = failedStep?.stepOrder ?? null;
  const checkIsScreenshotPending = useCallback(
    (run: FailureRun): boolean => {
      return (
        stepOrder !== null &&
        run.status === "running" &&
        findRunStep(run, failure, stepOrder)?.screenshotStatus === "pending"
      );
    },
    [failure, stepOrder],
  );
  const run = useGetFailureRun(
    project.key,
    failure.latestRunId,
    failedStep !== null,
    checkIsScreenshotPending,
  );
  const runPath = buildFailureRunPath(project.key, failure.latestRunId);

  if (failedStep === null) {
    return (
      <DSCard title={t("step.title")}>
        <div className={styles.content}>
          <DSText size="sm" color="muted">
            {t("step.none")}
          </DSText>
          <div>
            <DSButtonLink href={runPath} type="default">
              {t("step.openRun")}
            </DSButtonLink>
          </div>
        </div>
      </DSCard>
    );
  }

  const runStep =
    run.data === undefined ? null : findRunStep(run.data, failure, failedStep.stepOrder);

  return (
    <DSCard title={t("step.title")}>
      <div className={styles.content}>
        <DSText weight="medium">{t("step.order", { order: failedStep.stepOrder })}</DSText>
        <dl className={styles.fields}>
          {runStep !== null && (
            <div className={styles.field}>
              <dt className={styles.label}>{t("step.action")}</dt>
              <dd className={styles.value}>{runStep.action}</dd>
            </div>
          )}
          {runStep !== null && runStep.expected !== null && (
            <div className={styles.field}>
              <dt className={styles.label}>{t("step.expected")}</dt>
              <dd className={styles.value}>{runStep.expected}</dd>
            </div>
          )}
          <div className={styles.field}>
            <dt className={styles.label}>{t("step.actual")}</dt>
            <dd className={styles.value}>{failedStep.actualResult}</dd>
          </div>
          {failedStep.error !== null && (
            <div className={styles.field}>
              <dt className={styles.label}>{t("step.error")}</dt>
              <dd className={styles.value}>
                <DSCode isBlock>{failedStep.error}</DSCode>
              </dd>
            </div>
          )}
        </dl>
        <FailureScreenshot
          failedStep={failedStep}
          runStep={runStep}
          runStatus={run.data?.status ?? null}
        />
      </div>
    </DSCard>
  );
};
