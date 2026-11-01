import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { PROJECT_NAVIGATION_ITEMS } from "../typing/constants/navigation.constant";

export const buildProjectHref = (projectKey: string, segment: string): string => {
  const projectHref = `/projects/${encodeURIComponent(projectKey)}`;

  return segment === "" ? projectHref : `${projectHref}/${segment}`;
};

export const checkIsActiveRoute = (
  pathname: string,
  href: string,
  isExactMatch: boolean,
): boolean => {
  if (pathname === href) {
    return true;
  }

  if (isExactMatch) {
    return false;
  }

  const prefix = href.endsWith("/") ? href : `${href}/`;

  return pathname.startsWith(prefix);
};

export const readProjectSection = (pathname: string, projectKey: string): string => {
  const projectPrefix = `${buildProjectHref(projectKey, "")}/`;

  if (!pathname.startsWith(projectPrefix)) {
    return "";
  }

  const [section = ""] = pathname.slice(projectPrefix.length).split("/");

  return section;
};

export const buildProjectSwitchHref = (
  pathname: string,
  currentProjectKey: string | null,
  targetProject: Pick<Project, "key" | "capabilities">,
): string => {
  const section = currentProjectKey === null ? "" : readProjectSection(pathname, currentProjectKey);
  const navigationItem = PROJECT_NAVIGATION_ITEMS.find((item) => {
    return item.segment === section;
  });

  if (
    section === "" ||
    navigationItem === undefined ||
    !checkHasProjectCapability(targetProject, navigationItem.capability)
  ) {
    return buildProjectHref(targetProject.key, "");
  }

  return buildProjectHref(targetProject.key, section);
};
