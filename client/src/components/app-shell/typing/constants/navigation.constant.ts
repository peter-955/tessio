import type { ProjectNavigationItem, WorkspaceNavigationItem } from "../types/navigation.type";

export const PROJECT_NAVIGATION_ITEMS: ProjectNavigationItem[] = [
  { segment: "", labelKey: "dashboard", icon: "dashboard", capability: "project.view" },
  { segment: "sprints", labelKey: "sprints", icon: "sprints", capability: "sprint.view" },
  { segment: "stories", labelKey: "stories", icon: "stories", capability: "story.view" },
  { segment: "test-cases", labelKey: "testCases", icon: "testCases", capability: "test_case.view" },
  {
    segment: "shared-steps",
    labelKey: "sharedSteps",
    icon: "sharedSteps",
    capability: "test_case.view",
  },
  { segment: "suites", labelKey: "suites", icon: "suites", capability: "test_case.view" },
  { segment: "runs", labelKey: "runs", icon: "runs", capability: "run.view" },
  { segment: "plans", labelKey: "plans", icon: "plans", capability: "report.view" },
  { segment: "failures", labelKey: "failures", icon: "failures", capability: "failure.view" },
  { segment: "insights", labelKey: "insights", icon: "insights", capability: "report.view" },
  { segment: "test-data", labelKey: "testData", icon: "testData", capability: "test_data.view" },
  { segment: "members", labelKey: "members", icon: "members", capability: "project.view" },
  { segment: "settings", labelKey: "settings", icon: "settings", capability: "project.edit" },
];

export const WORKSPACE_NAVIGATION_ITEMS: WorkspaceNavigationItem[] = [
  { href: "/projects", labelKey: "projects", icon: "projects", isWorkspaceAdminOnly: false },
  { href: "/ai-harness", labelKey: "aiHarness", icon: "harness", isWorkspaceAdminOnly: false },
  { href: "/users", labelKey: "users", icon: "members", isWorkspaceAdminOnly: true },
  {
    href: "/settings",
    labelKey: "workspaceSettings",
    icon: "settings",
    isWorkspaceAdminOnly: true,
  },
];
