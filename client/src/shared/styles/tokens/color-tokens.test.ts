import { getContrastRatio, mixHexColors } from "@/test/utils/color-contrast.util";
import { readColorTokens, resolveMantineColor } from "@/test/utils/color-token.util";
import { describe, expect, it } from "vitest";

type ColorScheme = "light" | "dark";

const TEXT_CONTRAST = 4.5;

const NON_TEXT_CONTRAST = 3;

const COLOR_SCHEMES: readonly ColorScheme[] = ["light", "dark"];

const TEXT_TOKENS = ["text", "text-muted", "accent", "danger", "success", "warning"] as const;

const BACKGROUND_TOKENS = ["background", "surface", "surface-muted"] as const;

const SOFT_PAIRS = [
  ["danger", "danger-soft"],
  ["success", "success-soft"],
  ["warning", "warning-soft"],
  ["accent", "accent-soft"],
] as const;

const STATUS_TEXT_COLORS = ["red", "green", "yellow"] as const;

const FILLED_BUTTON_COLORS = [
  ["tessio", 6],
  ["red", 8],
] as const;

const DARK_LIGHT_VARIANT_WEIGHT = 0.5;

const tokens = readColorTokens();

const readToken = (name: string, scheme: ColorScheme): string => {
  const token = tokens[`--color-${name}`];
  if (token === undefined) {
    throw new Error(`Missing colour token --color-${name}`);
  }

  return token[scheme];
};

const BLACK = "#000000";

const WHITE = "#ffffff";

describe.each(COLOR_SCHEMES)("colour tokens in the %s scheme", (scheme) => {
  const textPairs = TEXT_TOKENS.flatMap((text) => {
    return BACKGROUND_TOKENS.map((background) => [text, background] as const);
  });

  it.each(textPairs)("%s on %s reaches 4.5:1", (text, background) => {
    expect(
      getContrastRatio(readToken(text, scheme), readToken(background, scheme)),
    ).toBeGreaterThanOrEqual(TEXT_CONTRAST);
  });

  it.each(SOFT_PAIRS)("%s on %s reaches 4.5:1", (text, background) => {
    expect(
      getContrastRatio(readToken(text, scheme), readToken(background, scheme)),
    ).toBeGreaterThanOrEqual(TEXT_CONTRAST);
  });

  it.each(["surface", "background"] as const)("input-border on %s reaches 3:1", (background) => {
    expect(
      getContrastRatio(readToken("input-border", scheme), readToken(background, scheme)),
    ).toBeGreaterThanOrEqual(NON_TEXT_CONTRAST);
  });

  it.each(STATUS_TEXT_COLORS)(
    "%s-text reaches 4.5:1 on the Mantine light-variant background",
    (color) => {
      const lightVariantBackground =
        scheme === "light"
          ? resolveMantineColor(color, 1)
          : mixHexColors(resolveMantineColor(color, 9), BLACK, DARK_LIGHT_VARIANT_WEIGHT);

      expect(
        getContrastRatio(readToken(`${color}-text`, scheme), lightVariantBackground),
      ).toBeGreaterThanOrEqual(TEXT_CONTRAST);
    },
  );
});

describe("filled button colours", () => {
  it.each(FILLED_BUTTON_COLORS)("white text on %s-%i reaches 4.5:1", (color, shade) => {
    expect(getContrastRatio(WHITE, resolveMantineColor(color, shade))).toBeGreaterThanOrEqual(
      TEXT_CONTRAST,
    );
  });
});

describe("contrast helpers", () => {
  it("computes the WCAG ratio of black on white", () => {
    expect(getContrastRatio(BLACK, WHITE)).toBeCloseTo(21, 5);
  });

  it("mixes in sRGB like color-mix", () => {
    expect(mixHexColors(WHITE, BLACK, 0.5)).toBe("#808080");
  });
});
