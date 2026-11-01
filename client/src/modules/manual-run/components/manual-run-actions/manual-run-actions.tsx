"use client";

import { DSButtonLink, DSGroup } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ManualRunActionsRun } from "../../typing/types/manual-run-actions-run.type";
import { buildRecordManualRunPath } from "../../utils/manual-run-path.util";
import { checkCanRecordRun, checkCanRerunFailed } from "../../utils/manual-run-permission.util";
import { RerunFailedButton } from "../rerun-failed-button/rerun-failed-button";

interface Props {
  run: ManualRunActionsRun;
}

export const ManualRunActions: FC<Props> = ({ run }) => {
  const { t } = useTranslation("manualRun");
  const project = useCurrentProject();
  const currentUser = useCurrentUser();
  const canRecord = checkCanRecordRun(project, run, currentUser.id);
  const canRerun = checkCanRerunFailed(project, run);

  if (!canRecord && !canRerun) {
    return null;
  }

  return (
    <DSGroup gap={2} isWrapping>
      {canRecord && (
        <DSButtonLink
          href={buildRecordManualRunPath(project.key, run.id)}
          type="primary"
          icon="runs"
        >
          {t("actions.continue")}
        </DSButtonLink>
      )}
      {canRerun && <RerunFailedButton run={run} />}
    </DSGroup>
  );
};
