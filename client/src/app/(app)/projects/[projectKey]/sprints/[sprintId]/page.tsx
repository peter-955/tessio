import { SprintDetailPage } from "@/modules/sprints/sprint-detail";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Sprint" };

const SprintRoute: FC<PageProps<"/projects/[projectKey]/sprints/[sprintId]">> = async ({
  params,
}) => {
  const { sprintId } = await params;

  return <SprintDetailPage sprintId={sprintId} />;
};

export default SprintRoute;
