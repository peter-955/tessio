"use client";

import { DSSkeleton, DSText } from "@/components/design-system";
import { useLastProjectKey } from "@/components/project-context/hooks/use-last-project-key";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { useGetProject } from "@/shared/hooks/queries/use-get-project";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useActiveProjectKey } from "../../hooks/use-active-project-key";
import { PROJECT_NAVIGATION_ITEMS } from "../../typing/constants/navigation.constant";
import { buildProjectHref, checkIsActiveRoute } from "../../utils/navigation.util";
import { NavigationLink } from "../navigation-link/navigation-link";
import styles from "./project-navigation.module.scss";

interface Props {
  onNavigate?: () => void;
}

export const ProjectNavigation: FC<Props> = ({ onNavigate }) => {
  const { t } = useTranslation();
  const { t: translateNavigation } = useTranslation("navigation");
  const pathname = usePathname();
  const projectKey = useActiveProjectKey();
  const { forgetProjectKey } = useLastProjectKey();
  const { data: project, error, isPending } = useGetProject(projectKey);
  const isProjectMissing = error?.status === 404;

  useEffect(() => {
    if (isProjectMissing && projectKey !== null) {
      forgetProjectKey(projectKey);
    }
  }, [forgetProjectKey, isProjectMissing, projectKey]);

  if (projectKey !== null && isPending) {
    return <DSSkeleton lineCount={6} />;
  }

  if (projectKey === null || isProjectMissing || project === undefined) {
    return (
      <div className={styles.hint}>
        <DSText size="sm" color="muted">
          {t("appShell.noProject.description")}
        </DSText>
        <Link href="/projects" className={styles.hintLink} onClick={onNavigate}>
          {t("appShell.projectSwitcher.allProjects")}
        </Link>
      </div>
    );
  }

  const visibleItems = PROJECT_NAVIGATION_ITEMS.filter((item) => {
    return checkHasProjectCapability(project, item.capability);
  });

  return (
    <nav aria-label={t("appShell.projectNavigation")} className={styles.navigation}>
      <DSText size="xs" color="muted" weight="medium" className={styles.heading}>
        {project.name}
      </DSText>
      {visibleItems.map((item) => {
        const href = buildProjectHref(project.key, item.segment);
        return (
          <NavigationLink
            key={item.segment}
            href={href}
            icon={item.icon}
            label={translateNavigation(item.labelKey)}
            isActive={checkIsActiveRoute(pathname, href, item.segment === "")}
            onNavigate={onNavigate}
          />
        );
      })}
    </nav>
  );
};
