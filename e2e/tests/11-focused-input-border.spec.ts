import type { Locator, Page } from "@playwright/test";
import type { InputBorderColors } from "../support/types/rgba-color.type.ts";
import { PROJECT_KEY } from "../support/constants/e2e-project.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import {
  contrastRatio,
  isSameColor,
  readInputBorderColors,
} from "../support/utils/color-contrast.util.ts";

const MINIMUM_NON_TEXT_CONTRAST = 3;
const COLOR_SCHEMES = ["light", "dark"] as const;

const expectColorScheme = async (page: Page, colorScheme: string): Promise<void> => {
  await expect(page.locator("html")).toHaveAttribute("data-mantine-color-scheme", colorScheme);
};

const countRunningAnimations = async (input: Locator): Promise<number> =>
  input.evaluate(
    (element) => (element.closest(".mantine-Input-input") ?? element).getAnimations().length,
  );

const readSettledBorderColors = async (input: Locator): Promise<InputBorderColors> => {
  await expect.poll(() => countRunningAnimations(input)).toBe(0);
  let previous = await readInputBorderColors(input);
  await expect
    .poll(async () => {
      const current = await readInputBorderColors(input);
      const isSettled =
        isSameColor(current.border, previous.border) &&
        isSameColor(current.background, previous.background);
      previous = current;
      return isSettled;
    })
    .toBe(true);
  return previous;
};

const expectVisibleFocusBorder = async (input: Locator, inputName: string): Promise<void> => {
  await expect(input).toBeVisible();
  await input.evaluate((element) => {
    if (element instanceof HTMLElement) {
      element.blur();
    }
  });
  await expect(input).not.toBeFocused();
  const unfocused = await readSettledBorderColors(input);
  await input.focus();
  await expect(input).toBeFocused();
  await expect
    .poll(async () => isSameColor((await readInputBorderColors(input)).border, unfocused.border), {
      message: `${inputName}: the border colour does not change on focus`,
    })
    .toBe(false);
  const focused = await readSettledBorderColors(input);
  expect(
    contrastRatio(focused.border, focused.background),
    `${inputName}: focused border contrast with the input background`,
  ).toBeGreaterThanOrEqual(MINIMUM_NON_TEXT_CONTRAST);
};

for (const colorScheme of COLOR_SCHEMES) {
  test.describe(`focused input border in the ${colorScheme} theme`, () => {
    test.use({ colorScheme });

    test("sign-in inputs show a visible focus border", async ({ page }) => {
      await page.goto("/sign-in");
      await expectColorScheme(page, colorScheme);
      await expect(page.getByRole("textbox", { name: "Email", exact: true })).toBeFocused();
      await expectVisibleFocusBorder(
        page.getByRole("textbox", { name: "Email", exact: true }),
        "Email (DSInput)",
      );
      await expectVisibleFocusBorder(
        page.getByRole("textbox", { name: "Password", exact: true }),
        "Password (DSPasswordInput)",
      );
    });

    test("test case form inputs show a visible focus border", async ({ qcPage }) => {
      await qcPage.goto(`/projects/${PROJECT_KEY}/test-cases/new`);
      await expectColorScheme(qcPage, colorScheme);
      await expectVisibleFocusBorder(
        qcPage.getByRole("combobox", { name: "Story" }),
        "Story (DSSelect)",
      );
      await expectVisibleFocusBorder(
        qcPage.getByRole("textbox", { name: "Title" }),
        "Title (DSInput)",
      );
      await expectVisibleFocusBorder(
        qcPage.getByRole("textbox", { name: "Business value" }),
        "Business value (DSTextarea)",
      );
    });
  });
}
