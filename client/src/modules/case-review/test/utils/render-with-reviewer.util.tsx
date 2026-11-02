import type { Project } from "@/components/project-context/typing/types/project.type";
import { SessionGuardContext } from "@/components/session-guard/session-guard.context";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { renderWithProject } from "@/modules/test-cases/test/utils/render-with-project.util";
import type { ReactElement } from "react";
import { buildCurrentUser } from "./current-user-fixture.util";

export const renderWithReviewer = (
  element: ReactElement,
  project: Project,
  currentUser: CurrentUser = buildCurrentUser(),
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <SessionGuardContext value={currentUser}>{element}</SessionGuardContext>,
    project,
  );
};
