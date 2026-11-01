import { MISSING_TEST_DATA_TYPE } from "../typing/constants/gap.constant";
import type { RaiseGapBody } from "../typing/types/gap.type";
import type { RaiseGapInput } from "../typing/types/raise-gap-values.type";

export const buildRaiseGapBody = (values: RaiseGapInput): RaiseGapBody => {
  return {
    type: values.type,
    severity: values.severity,
    targetType: values.targetType,
    question: values.question.trim(),
    assigneeId: values.assigneeId,
    ...(values.targetType === "story" ? {} : { targetRef: values.targetRef }),
    ...(values.type === MISSING_TEST_DATA_TYPE ? { dataScope: values.dataScope } : {}),
  };
};
