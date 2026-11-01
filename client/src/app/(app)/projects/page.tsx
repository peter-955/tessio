import { ProjectsPage } from "@/modules/projects/projects";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Projects" };

const ProjectsRoute: FC = () => {
  return <ProjectsPage />;
};

export default ProjectsRoute;
