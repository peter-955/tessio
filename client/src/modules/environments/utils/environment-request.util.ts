import type { EnvironmentFormValues } from "../typing/types/environment-form-values.type";
import type { Environment, EnvironmentRequest } from "../typing/types/environment.type";

export const buildEnvironmentFormValues = (
  environment: Environment | null,
): EnvironmentFormValues => {
  return {
    name: environment?.name ?? "",
    baseUrl: environment?.baseUrl ?? "",
    healthCheckUrl: environment?.healthCheckUrl ?? "",
  };
};

export const buildEnvironmentRequest = (values: EnvironmentFormValues): EnvironmentRequest => {
  const healthCheckUrl = values.healthCheckUrl.trim();

  return {
    name: values.name.trim(),
    baseUrl: values.baseUrl.trim(),
    healthCheckUrl: healthCheckUrl === "" ? null : healthCheckUrl,
  };
};
