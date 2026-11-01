import { ProjectGate } from "@/components/project-context/project-gate/project-gate";
import type { FC } from "react";

const ProjectLayout: FC<LayoutProps<"/projects/[projectKey]">> = async ({ children, params }) => {
  const { projectKey } = await params;

  return <ProjectGate projectKey={projectKey}>{children}</ProjectGate>;
};

export default ProjectLayout;
