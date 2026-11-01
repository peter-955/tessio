import type { Locator } from "@playwright/test";
import type { InputBorderColors, RgbaColor } from "../types/rgba-color.type.ts";

const LINEAR_THRESHOLD = 0.04045;
const MAXIMUM_CHANNEL = 255;
const CONTRAST_OFFSET = 0.05;

export const readInputBorderColors = async (locator: Locator): Promise<InputBorderColors> => {
  return locator.evaluate((element): InputBorderColors => {
    const inputElement = element.closest(".mantine-Input-input") ?? element;
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (context === null) {
      throw new Error("The canvas has no 2d context");
    }
    const toRgba = (cssColor: string): RgbaColor => {
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = "rgba(0, 0, 0, 0)";
      context.fillStyle = cssColor;
      context.fillRect(0, 0, 1, 1);
      const [red = 0, green = 0, blue = 0, alpha = 0] = context.getImageData(0, 0, 1, 1).data;
      return { red, green, blue, alpha: alpha / 255 };
    };
    const blend = (top: RgbaColor, bottom: RgbaColor): RgbaColor => ({
      red: top.red * top.alpha + bottom.red * (1 - top.alpha),
      green: top.green * top.alpha + bottom.green * (1 - top.alpha),
      blue: top.blue * top.alpha + bottom.blue * (1 - top.alpha),
      alpha: 1,
    });
    const inputStyle = getComputedStyle(inputElement);
    const bodyBackground = blend(toRgba(getComputedStyle(document.body).backgroundColor), {
      red: 255,
      green: 255,
      blue: 255,
      alpha: 1,
    });
    const background = blend(toRgba(inputStyle.backgroundColor), bodyBackground);
    const border = blend(toRgba(inputStyle.borderTopColor), background);
    return { border, background };
  });
};

const toLinearChannel = (channel: number): number => {
  const normalized = channel / MAXIMUM_CHANNEL;
  return normalized <= LINEAR_THRESHOLD
    ? normalized / 12.92
    : ((normalized + 0.055) / 1.055) ** 2.4;
};

const relativeLuminance = (color: RgbaColor): number =>
  0.2126 * toLinearChannel(color.red) +
  0.7152 * toLinearChannel(color.green) +
  0.0722 * toLinearChannel(color.blue);

export const contrastRatio = (first: RgbaColor, second: RgbaColor): number => {
  const firstLuminance = relativeLuminance(first);
  const secondLuminance = relativeLuminance(second);
  const lighter = Math.max(firstLuminance, secondLuminance);
  const darker = Math.min(firstLuminance, secondLuminance);
  return (lighter + CONTRAST_OFFSET) / (darker + CONTRAST_OFFSET);
};

export const isSameColor = (first: RgbaColor, second: RgbaColor): boolean =>
  Math.round(first.red) === Math.round(second.red) &&
  Math.round(first.green) === Math.round(second.green) &&
  Math.round(first.blue) === Math.round(second.blue);
