import { ProjectMembersPage } from "@/modules/projects/project-members";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Members" };

const ProjectMembersRoute: FC = () => {
  return <ProjectMembersPage />;
};

export default ProjectMembersRoute;
