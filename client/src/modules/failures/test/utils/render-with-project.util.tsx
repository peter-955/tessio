import { ProjectContext } from "@/components/project-context/contexts/project.context";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import type { QueryClient } from "@tanstack/react-query";
import { render, type RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";

interface Result extends RenderResult {
  queryClient: QueryClient;
  rerenderWithProject: (element: ReactElement) => void;
}

export const renderWithProject = (element: ReactElement, project: Project): Result => {
  const queryClient = createTestQueryClient();
  const wrap = (child: ReactElement): ReactElement => {
    return (
      <TestProviders queryClient={queryClient}>
        <ProjectContext value={project}>{child}</ProjectContext>
      </TestProviders>
    );
  };
  const result = render(wrap(element));

  return {
    ...result,
    queryClient,
    rerenderWithProject: (nextElement: ReactElement): void => {
      result.rerender(wrap(nextElement));
    },
  };
};
