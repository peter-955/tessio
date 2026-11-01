import type { WorkspaceRole } from "@/components/app-shell/typing/types/workspace-role.type";
import { ProjectContext } from "@/components/project-context/contexts/project.context";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { SessionGuardContext } from "@/components/session-guard/session-guard.context";
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import type { QueryClient } from "@tanstack/react-query";
import { render, type RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";
import { buildCurrentUser } from "./current-user.fixture";

interface Options {
  workspaceRole?: WorkspaceRole;
  project?: Project;
  queryClient?: QueryClient;
}

interface Result extends RenderResult {
  queryClient: QueryClient;
}

export const renderWithContext = (
  element: ReactElement,
  { workspaceRole = "member", project, queryClient = createTestQueryClient() }: Options = {},
): Result => {
  const projectElement =
    project === undefined ? element : <ProjectContext value={project}>{element}</ProjectContext>;
  const result = render(
    <TestProviders queryClient={queryClient}>
      <SessionGuardContext value={buildCurrentUser(workspaceRole)}>
        {projectElement}
      </SessionGuardContext>
    </TestProviders>,
  );

  return { ...result, queryClient };
};
