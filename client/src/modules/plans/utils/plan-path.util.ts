import { buildProjectPath } from "@/modules/projects/utils/project-path.util";

export const buildPlansPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "plans");
};

export const buildPlanPath = (projectKey: string, planId: string): string => {
  return `${buildPlansPath(projectKey)}/${encodeURIComponent(planId)}`;
};

export const buildPlanSuitePath = (projectKey: string, suiteId: string): string => {
  return buildProjectPath(projectKey, `suites/${encodeURIComponent(suiteId)}`);
};
