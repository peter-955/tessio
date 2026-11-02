"use client";

import { ReferenceText } from "@/components/case-sheet/reference-text/reference-text";
import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import { DSStepTimeline, type DSStepTimelineStep } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type { SharedStepAction } from "../../typing/types/shared-step.type";
import { sortSharedStepActions } from "../../utils/shared-step-form.util";

interface Props {
  actions: readonly SharedStepAction[];
  ariaLabel: string;
  references?: CaseReferences;
}

export const SharedStepActions: FC<Props> = ({ actions, ariaLabel, references }) => {
  const { t } = useTranslation("sharedSteps");

  const renderText = (text: string): ReactNode => {
    return references === undefined ? text : <ReferenceText text={text} references={references} />;
  };

  const steps = sortSharedStepActions(actions).map((action): DSStepTimelineStep => {
    return {
      key: String(action.order),
      order: action.order,
      action: renderText(action.action),
      expected:
        action.expected === null || action.expected === "" ? null : renderText(action.expected),
    };
  });

  return (
    <DSStepTimeline
      steps={steps}
      labels={{ step: (order) => t("steps.step", { order }), expected: t("steps.expected") }}
      ariaLabel={ariaLabel}
    />
  );
};
