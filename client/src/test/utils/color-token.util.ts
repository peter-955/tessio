import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { DEFAULT_THEME, type MantineColorsTuple } from "@mantine/core";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { mixHexColors } from "./color-contrast.util";

const COLOR_TOKEN_FILE = join("src", "shared", "styles", "tokens", "color.css");

const TOKEN_DECLARATION_PATTERN = /(--color-[a-z0-9-]+)\s*:\s*([^;]+);/g;

const PALETTE_VARIABLE_PATTERN = /^var\(--mantine-color-([a-z]+)-(\d)\)$/;

const PERCENTAGE_PATTERN = /^(.+?)\s+(\d+(?:\.\d+)?)%$/;

const NAMED_COLORS: Readonly<Record<string, string>> = {
  black: "#000000",
  white: "#ffffff",
  "var(--mantine-color-black)": "#000000",
  "var(--mantine-color-white)": "#ffffff",
};

const MANTINE_PALETTES: Readonly<Record<string, MantineColorsTuple | undefined>> = {
  ...DEFAULT_THEME.colors,
  ...mantineTheme.colors,
};

const splitTopLevelArguments = (value: string): string[] => {
  const parts: string[] = [];
  let depth = 0;
  let current = "";
  for (const character of value) {
    if (character === "(") {
      depth += 1;
    }
    if (character === ")") {
      depth -= 1;
    }
    if (character === "," && depth === 0) {
      parts.push(current.trim());
      current = "";
      continue;
    }
    current += character;
  }
  if (depth !== 0) {
    throw new Error(`Unbalanced parentheses in: ${value}`);
  }
  parts.push(current.trim());

  return parts;
};

const readFunctionArguments = (expression: string, functionName: string): string[] | null => {
  const prefix = `${functionName}(`;
  if (!expression.startsWith(prefix) || !expression.endsWith(")")) {
    return null;
  }

  return splitTopLevelArguments(expression.slice(prefix.length, -1));
};

const parseWeightedColor = (argument: string): { expression: string; weight: number | null } => {
  const match = PERCENTAGE_PATTERN.exec(argument);
  if (match === null) {
    return { expression: argument, weight: null };
  }

  return { expression: match[1].trim(), weight: Number(match[2]) / 100 };
};

export const resolveMantineColor = (name: string, shade: number): string => {
  const palette = MANTINE_PALETTES[name];
  const color = palette?.[shade];
  if (color === undefined) {
    throw new Error(`Unknown Mantine colour: ${name}-${shade}`);
  }

  return color;
};

export const resolveColorExpression = (expression: string): string => {
  const normalized = expression.replace(/\s+/g, " ").trim();
  const namedColor = NAMED_COLORS[normalized];
  if (namedColor !== undefined) {
    return namedColor;
  }
  const paletteMatch = PALETTE_VARIABLE_PATTERN.exec(normalized);
  if (paletteMatch !== null) {
    return resolveMantineColor(paletteMatch[1], Number(paletteMatch[2]));
  }
  const mixArguments = readFunctionArguments(normalized, "color-mix");
  if (mixArguments !== null) {
    const [space, firstArgument, secondArgument] = mixArguments;
    if (space !== "in srgb" || mixArguments.length !== 3) {
      throw new Error(`Unsupported color-mix: ${normalized}`);
    }
    const first = parseWeightedColor(firstArgument);
    const second = parseWeightedColor(secondArgument);
    const firstWeight = first.weight ?? (second.weight === null ? 0.5 : 1 - second.weight);

    return mixHexColors(
      resolveColorExpression(first.expression),
      resolveColorExpression(second.expression),
      firstWeight,
    );
  }

  throw new Error(`Cannot resolve the colour expression: ${normalized}`);
};

export const readColorTokens = (): Record<string, { light: string; dark: string }> => {
  const source = readFileSync(join(process.cwd(), COLOR_TOKEN_FILE), "utf8");
  const tokens: Record<string, { light: string; dark: string }> = {};
  for (const [, name, value] of source.matchAll(TOKEN_DECLARATION_PATTERN)) {
    const schemeArguments = readFunctionArguments(value.replace(/\s+/g, " ").trim(), "light-dark");
    if (schemeArguments === null || schemeArguments.length !== 2) {
      throw new Error(`The token ${name} is not a light-dark() pair: ${value}`);
    }
    tokens[name] = {
      light: resolveColorExpression(schemeArguments[0]),
      dark: resolveColorExpression(schemeArguments[1]),
    };
  }
  if (Object.keys(tokens).length === 0) {
    throw new Error(`No colour tokens found in ${COLOR_TOKEN_FILE}`);
  }

  return tokens;
};
