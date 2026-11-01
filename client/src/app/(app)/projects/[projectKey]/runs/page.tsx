import { NewManualRunButtonLink } from "@/modules/manual-run/components/new-manual-run-button-link/new-manual-run-button-link";
import { RunsPage } from "@/modules/runs/runs";
import { parseRunFilters } from "@/modules/runs/utils/run-filters.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Runs" };

const RunsRoute: FC<PageProps<"/projects/[projectKey]/runs">> = async ({ searchParams }) => {
  return (
    <RunsPage
      initialFilters={parseRunFilters(await searchParams)}
      actions={<NewManualRunButtonLink />}
    />
  );
};

export default RunsRoute;
