import { DashboardPage } from "@/modules/dashboard/dashboard";
import { parseDashboardSprintId } from "@/modules/dashboard/utils/dashboard-search.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Dashboard" };

const ProjectDashboardRoute: FC<PageProps<"/projects/[projectKey]">> = async ({ searchParams }) => {
  return <DashboardPage initialSprintId={parseDashboardSprintId(await searchParams)} />;
};

export default ProjectDashboardRoute;
