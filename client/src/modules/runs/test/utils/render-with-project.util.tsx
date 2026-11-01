import { ProjectContext } from "@/components/project-context/contexts/project.context";
import { buildProject } from "@/components/project-context/test/utils/project-fixture.util";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import type { QueryClient } from "@tanstack/react-query";
import type { RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";

interface Result extends RenderResult {
  queryClient: QueryClient;
}

export const TEST_PROJECT_KEY = "APP";

export const renderWithProject = (
  element: ReactElement,
  projectOverrides: Partial<Project> = {},
): Result => {
  return renderWithProviders(
    <ProjectContext
      value={buildProject({
        key: TEST_PROJECT_KEY,
        jiraProjectKey: TEST_PROJECT_KEY,
        ...projectOverrides,
      })}
    >
      {element}
    </ProjectContext>,
  );
};
