import type { Page } from "@playwright/test";
import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import { CASE, PROJECT_KEY } from "../support/constants/e2e-project.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import type { LayoutScreen } from "../support/types/layout-screen.type.ts";
import { expectNoHorizontalScroll } from "../support/utils/layout.util.ts";
import { requireRunValue } from "../support/utils/run-state.util.ts";

const PROJECT_PATH = `/projects/${PROJECT_KEY}`;

const buildQcScreens = (): LayoutScreen[] => {
  const caseCode = requireRunValue("caseCode");
  return [
    { path: "/projects", heading: "Projects" },
    { path: PROJECT_PATH, heading: "Dashboard" },
    { path: `${PROJECT_PATH}/stories`, heading: "Stories" },
    {
      path: `${PROJECT_PATH}/stories/${SAVED_CARD_STORY.key}`,
      heading: `${SAVED_CARD_STORY.key} · ${SAVED_CARD_STORY.summary}`,
    },
    { path: `${PROJECT_PATH}/test-cases`, heading: "Test cases" },
    { path: `${PROJECT_PATH}/test-cases/${caseCode}`, heading: new RegExp(CASE.title) },
    { path: `${PROJECT_PATH}/runs`, heading: "Runs" },
    {
      path: `${PROJECT_PATH}/runs/${requireRunValue("firstRunId")}`,
      heading: `Run on ${SAVED_CARD_STORY.key}`,
    },
    { path: `${PROJECT_PATH}/failures`, heading: "Failures" },
    {
      path: `${PROJECT_PATH}/failures/${requireRunValue("failureId")}`,
      heading: `${caseCode} · ${CASE.title}`,
    },
    { path: `${PROJECT_PATH}/test-data`, heading: "Test data" },
    { path: "/gaps", heading: "My gaps" },
    { path: "/profile", heading: "Profile" },
  ];
};

const OWNER_SCREENS: LayoutScreen[] = [
  { path: "/users", heading: "Users" },
  { path: "/settings", heading: "Workspace settings" },
  { path: `${PROJECT_PATH}/members`, heading: "Members" },
];

const checkScreens = async (page: Page, screens: LayoutScreen[]): Promise<void> => {
  for (const screen of screens) {
    await test.step(screen.path, async () => {
      await page.goto(screen.path);
      await expect
        .soft(page.getByRole("heading", { level: 1, name: screen.heading }), screen.path)
        .toBeVisible();
      await expectNoHorizontalScroll(page);
    });
  }
};

test.describe("phone layout at 375 px", () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test("the QC screens fit the phone width", async ({ qcPage }) => {
    await checkScreens(qcPage, buildQcScreens());
  });

  test("the owner screens fit the phone width", async ({ ownerPage }) => {
    await checkScreens(ownerPage, OWNER_SCREENS);
  });

  test("the sign-in screen fits the phone width", async ({ page }) => {
    await checkScreens(page, [{ path: "/sign-in", heading: "Sign in to Tessio" }]);
  });

  test("the navigation drawer opens and closes", async ({ qcPage }) => {
    await qcPage.goto(PROJECT_PATH);
    const storiesLink = qcPage.getByRole("link", { name: "Stories", exact: true });
    await expect(storiesLink).toBeHidden();
    await qcPage.getByRole("button", { name: "Open navigation" }).click();
    await expect(storiesLink).toBeVisible();
    await expectNoHorizontalScroll(qcPage);
    await qcPage.getByRole("button", { name: "Close navigation" }).click();
    await expect(storiesLink).toBeHidden();
  });
});
