import { ProjectSettingsPage } from "@/modules/projects/project-settings";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Project settings" };

const ProjectSettingsRoute: FC = () => {
  return <ProjectSettingsPage />;
};

export default ProjectSettingsRoute;
