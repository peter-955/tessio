import { RunsPageActions } from "@/modules/runs/components/runs-page-actions/runs-page-actions";
import { RunsPage } from "@/modules/runs/runs";
import { parseRunFilters } from "@/modules/runs/utils/run-filters.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Runs" };

const RunsRoute: FC<PageProps<"/projects/[projectKey]/runs">> = async ({ searchParams }) => {
  return (
    <RunsPage initialFilters={parseRunFilters(await searchParams)} actions={<RunsPageActions />} />
  );
};

export default RunsRoute;
