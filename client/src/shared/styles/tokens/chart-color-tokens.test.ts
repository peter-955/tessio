import { getContrastRatio } from "@/test/utils/color-contrast.util";
import { readColorTokens } from "@/test/utils/color-token.util";
import { describe, expect, it } from "vitest";

type ColorScheme = "light" | "dark";

const NON_TEXT_CONTRAST = 3;

const COLOR_SCHEMES: readonly ColorScheme[] = ["light", "dark"];

const CHART_TOKENS = ["chart-1", "chart-2", "chart-3", "chart-4", "chart-5"] as const;

const tokens = readColorTokens();

const readToken = (name: string, scheme: ColorScheme): string => {
  const token = tokens[`--color-${name}`];
  if (token === undefined) {
    throw new Error(`Missing colour token --color-${name}`);
  }

  return token[scheme];
};

describe.each(COLOR_SCHEMES)("chart colour tokens in the %s scheme", (scheme) => {
  it.each(CHART_TOKENS)("%s reaches 3:1 on surface", (chartToken) => {
    expect(
      getContrastRatio(readToken(chartToken, scheme), readToken("surface", scheme)),
    ).toBeGreaterThanOrEqual(NON_TEXT_CONTRAST);
  });

  it("gives every series a different colour", () => {
    const values = CHART_TOKENS.map((chartToken) => {
      return readToken(chartToken, scheme);
    });

    expect(new Set(values).size).toBe(CHART_TOKENS.length);
  });
});
