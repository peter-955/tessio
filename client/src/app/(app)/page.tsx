import { WorkspaceHomePage } from "@/modules/dashboard/workspace-home";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Dashboard" };

const WorkspaceHomeRoute: FC = () => {
  return <WorkspaceHomePage />;
};

export default WorkspaceHomeRoute;
