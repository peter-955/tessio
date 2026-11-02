"use client";

import { ReferenceText } from "@/components/case-sheet/reference-text/reference-text";
import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import {
  DSIcon,
  DSStepTimeline,
  DSText,
  type DSStepTimelineLabels,
  type DSStepTimelineStep,
} from "@/components/design-system";
import type { DataRow } from "@/modules/data-rows/typing/types/data-table.type";
import { fillParameters } from "@/modules/data-rows/utils/parameter-text.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ManualRunStep } from "../../typing/types/manual-run.type";
import styles from "./recorded-steps.module.scss";

interface Props {
  steps: readonly ManualRunStep[];
  references: CaseReferences;
  ariaLabel: string;
  values?: DataRow;
}

export const RecordedSteps: FC<Props> = ({ steps, references, ariaLabel, values = {} }) => {
  const { t } = useTranslation("manualRun");
  const labels: DSStepTimelineLabels = {
    step: (order) => t("record.step", { order }),
    expected: t("record.expected"),
    actualResult: t("record.actualResult"),
    error: t("record.error"),
  };

  if (steps.length === 0) {
    return <DSText color="muted">{t("record.noSteps")}</DSText>;
  }

  const timelineSteps = steps.map((step): DSStepTimelineStep => {
    return {
      key: String(step.order),
      order: step.order,
      action: <ReferenceText text={fillParameters(step.action, values)} references={references} />,
      expected:
        step.expected === null || step.expected === "" ? null : (
          <ReferenceText text={fillParameters(step.expected, values)} references={references} />
        ),
      status: step.status ?? "not_reported",
      statusLabel: step.status === null ? t("record.notReported") : t(`status.${step.status}`),
      actualResult: step.actualResult,
      error: step.error,
      media:
        step.evidenceFileId === null ? undefined : (
          <span className={styles.evidence}>
            <DSIcon name="file" size={16} />
            <DSText size="sm" component="span">
              {t("record.evidenceAttached")}
            </DSText>
          </span>
        ),
    };
  });

  return <DSStepTimeline steps={timelineSteps} labels={labels} ariaLabel={ariaLabel} />;
};
