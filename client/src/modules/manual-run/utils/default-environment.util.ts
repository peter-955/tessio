import type { RunEnvironment } from "../typing/types/manual-run.type";

export const pickDefaultEnvironmentId = (
  environments: readonly Pick<RunEnvironment, "id">[],
  defaultEnvironmentId: string | null,
): string | null => {
  const hasDefault = environments.some((environment) => {
    return environment.id === defaultEnvironmentId;
  });

  if (hasDefault) {
    return defaultEnvironmentId;
  }

  const [onlyEnvironment] = environments;

  return environments.length === 1 && onlyEnvironment !== undefined ? onlyEnvironment.id : null;
};
