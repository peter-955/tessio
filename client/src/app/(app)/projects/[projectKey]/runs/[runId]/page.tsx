import { RunManualActions } from "@/modules/runs/components/run-manual-actions/run-manual-actions";
import { RunDetailPage } from "@/modules/runs/run-detail";
import { parseRunDetailTab } from "@/modules/runs/utils/run-detail-tab.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Run" };

const RunRoute: FC<PageProps<"/projects/[projectKey]/runs/[runId]">> = async ({
  params,
  searchParams,
}) => {
  const { runId } = await params;
  const { tab } = await searchParams;

  return (
    <RunDetailPage
      runId={runId}
      initialTab={parseRunDetailTab(tab)}
      actions={<RunManualActions runId={runId} />}
    />
  );
};

export default RunRoute;
