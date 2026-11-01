"use client";

import { DSErrorState, DSSkeleton } from "@/components/design-system";
import { useLastProjectKey } from "@/components/project-context/hooks/use-last-project-key";
import { PROJECTS_PATH } from "@/modules/projects/typing/constants/project-path.constant";
import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import { useGetProjects } from "@/shared/hooks/queries/use-get-projects";
import { useRouter } from "next/navigation";
import { useEffect, type FC } from "react";
import { useTranslation } from "react-i18next";
import { selectLandingProjectKey } from "./utils/landing-project.util";

export const WorkspaceHomePage: FC = () => {
  const { t } = useTranslation("dashboard");
  const router = useRouter();
  const { lastProjectKey } = useLastProjectKey();
  const { data, isError, refetch } = useGetProjects();

  useEffect(() => {
    if (data === undefined) {
      return;
    }

    const projectKey = selectLandingProjectKey(data, lastProjectKey);
    router.replace(projectKey === null ? PROJECTS_PATH : buildProjectPath(projectKey));
  }, [data, lastProjectKey, router]);

  if (isError) {
    return (
      <DSErrorState
        title={t("home.loadError")}
        retryLabel={t("retry")}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  return (
    <div aria-busy="true">
      <DSSkeleton lineCount={6} />
    </div>
  );
};
