import type { Project } from "@/components/project-context/typing/types/project.type";

export const selectLandingProjectKey = (
  projects: Pick<Project, "key">[],
  lastProjectKey: string | null,
): string | null => {
  const isLastProjectVisible = projects.some((project) => {
    return project.key === lastProjectKey;
  });

  if (lastProjectKey !== null && isLastProjectVisible) {
    return lastProjectKey;
  }

  return projects[0]?.key ?? null;
};
