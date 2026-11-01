"use client";

import { DSButtonLink } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildNewManualRunPath } from "../../utils/manual-run-path.util";
import { checkCanStartManualRun } from "../../utils/manual-run-permission.util";

interface Props {
  storyKey?: string;
}

export const NewManualRunButtonLink: FC<Props> = ({ storyKey }) => {
  const { t } = useTranslation("manualRun");
  const project = useCurrentProject();

  if (!checkCanStartManualRun(project)) {
    return null;
  }

  return (
    <DSButtonLink href={buildNewManualRunPath(project.key, storyKey)} type="primary" icon="plus">
      {t("actions.newRun")}
    </DSButtonLink>
  );
};
