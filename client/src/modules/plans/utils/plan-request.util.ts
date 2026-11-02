import type { PlanFormValues } from "../typing/types/plan-form-values.type";
import type { PlanItemsFormValues } from "../typing/types/plan-items-form-values.type";
import type {
  CreatePlanRequest,
  PlanDetail,
  PlanItem,
  SetPlanItemsRequest,
  UpdatePlanRequest,
} from "../typing/types/plan.type";

type PlanFormSource = Pick<PlanDetail, "name" | "description" | "targetDate" | "environmentId">;

const toOptionalText = (value: string): string | null => {
  const trimmedValue = value.trim();

  return trimmedValue === "" ? null : trimmedValue;
};

export const buildPlanFormValues = (plan: PlanFormSource | null): PlanFormValues => {
  return {
    name: plan?.name ?? "",
    description: plan?.description ?? "",
    targetDate: plan?.targetDate ?? null,
    environmentId: plan?.environmentId ?? null,
  };
};

export const buildCreatePlanRequest = (values: PlanFormValues): CreatePlanRequest => {
  const description = toOptionalText(values.description);

  return {
    name: values.name.trim(),
    ...(description === null ? {} : { description }),
    ...(values.targetDate === null ? {} : { targetDate: values.targetDate }),
    ...(values.environmentId === null ? {} : { environmentId: values.environmentId }),
  };
};

export const buildUpdatePlanRequest = (
  values: PlanFormValues,
  plan: PlanFormSource,
): UpdatePlanRequest => {
  const name = values.name.trim();
  const description = toOptionalText(values.description);

  return {
    ...(name === plan.name ? {} : { name }),
    ...(description === plan.description ? {} : { description }),
    ...(values.targetDate === plan.targetDate ? {} : { targetDate: values.targetDate }),
    ...(values.environmentId === plan.environmentId ? {} : { environmentId: values.environmentId }),
  };
};

export const buildPlanItemsFormValues = (items: readonly PlanItem[]): PlanItemsFormValues => {
  return {
    suiteIds: items.flatMap((item) => {
      return item.kind === "suite" && item.suiteId !== null ? [item.suiteId] : [];
    }),
    storyIds: items.flatMap((item) => {
      return item.kind === "story" && item.storyId !== null ? [item.storyId] : [];
    }),
  };
};

export const buildSetPlanItemsRequest = (values: PlanItemsFormValues): SetPlanItemsRequest => {
  return {
    items: [
      ...values.suiteIds.map((suiteId) => {
        return { suiteId };
      }),
      ...values.storyIds.map((storyId) => {
        return { storyId };
      }),
    ],
  };
};

export const countPlanItems = (values: PlanItemsFormValues): number => {
  return values.suiteIds.length + values.storyIds.length;
};

export const checkHasSamePlanItems = (
  values: PlanItemsFormValues,
  items: readonly PlanItem[],
): boolean => {
  const current = buildSetPlanItemsRequest(buildPlanItemsFormValues(items)).items;
  const next = buildSetPlanItemsRequest(values).items;

  return JSON.stringify(current) === JSON.stringify(next);
};
