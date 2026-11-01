import { RecordManualRunPage } from "@/modules/manual-run/record-manual-run";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Record manual run" };

const RecordManualRunRoute: FC<PageProps<"/projects/[projectKey]/runs/[runId]/record">> = async ({
  params,
}) => {
  const { runId } = await params;

  return <RecordManualRunPage runId={runId} />;
};

export default RecordManualRunRoute;
