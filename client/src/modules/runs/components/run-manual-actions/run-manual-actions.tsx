"use client";

import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { ManualRunActions } from "@/modules/manual-run/components/manual-run-actions/manual-run-actions";
import type { FC } from "react";
import { useGetRun } from "../../hooks/queries/use-get-run";
import { RUN_ID_PATTERN } from "../../typing/constants/run.constant";

interface Props {
  runId: string;
}

export const RunManualActions: FC<Props> = ({ runId }) => {
  const project = useCurrentProject();
  const { data } = useGetRun(project.key, runId, RUN_ID_PATTERN.test(runId));

  if (data === undefined) {
    return null;
  }

  return (
    <ManualRunActions
      run={{
        id: data.id,
        executor: data.executor,
        status: data.status,
        startedBy: data.startedBy,
        failedCount: data.counts.failed,
        blockedCount: data.counts.blocked,
      }}
    />
  );
};
