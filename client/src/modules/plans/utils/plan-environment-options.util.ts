import type { DSSelectOption } from "@/components/design-system";
import type { components } from "@/lib/api/openapi.type";
import type { PlanDetail } from "../typing/types/plan.type";

type Environment = Pick<components["schemas"]["EnvironmentResponse"], "id" | "name">;

export const buildEnvironmentOptions = (
  environments: readonly Environment[],
  plan: Pick<PlanDetail, "environmentId" | "environmentName"> | null,
): DSSelectOption<string>[] => {
  const options = environments.map((environment): DSSelectOption<string> => {
    return { value: environment.id, label: environment.name };
  });
  const currentId = plan?.environmentId ?? null;
  if (
    currentId === null ||
    options.some((option) => {
      return option.value === currentId;
    })
  ) {
    return options;
  }

  return [...options, { value: currentId, label: plan?.environmentName ?? currentId }];
};
