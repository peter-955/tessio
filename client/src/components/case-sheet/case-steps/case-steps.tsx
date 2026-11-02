"use client";

import { DSStepTimeline, DSText, type DSStepTimelineStep } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ReferenceText } from "../reference-text/reference-text";
import type { CaseReferences, CaseStep } from "../typing/types/case-sheet.type";

interface Props {
  steps: readonly CaseStep[];
  references: CaseReferences;
  renderSharedStep?: (sharedStepKey: string) => ReactNode;
}

export const CaseSteps: FC<Props> = ({ steps, references, renderSharedStep }) => {
  const { t } = useTranslation("caseSheet");

  if (steps.length === 0) {
    return <DSText color="muted">{t("noSteps")}</DSText>;
  }

  const timelineSteps = steps.map((step): DSStepTimelineStep => {
    const sharedStepKey = step.sharedStepKey ?? null;
    if (sharedStepKey !== null && renderSharedStep !== undefined) {
      return {
        key: String(step.order),
        order: step.order,
        action: null,
        expected: null,
        details: renderSharedStep(sharedStepKey),
      };
    }

    return {
      key: String(step.order),
      order: step.order,
      action: <ReferenceText text={step.action ?? ""} references={references} />,
      expected:
        step.expected === null || step.expected === "" ? null : (
          <ReferenceText text={step.expected} references={references} />
        ),
    };
  });

  return (
    <DSStepTimeline
      steps={timelineSteps}
      labels={{ step: (order) => t("stepLabel", { order }), expected: t("expected") }}
      ariaLabel={t("steps")}
    />
  );
};
