import type { DSButtonStyle, DSButtonType } from "../types/button.type";

export const DS_BUTTON_STYLES: Record<DSButtonType, DSButtonStyle> = {
  primary: { variant: "filled" },
  default: { variant: "default" },
  outline: { variant: "outline" },
  ghost: { variant: "subtle", color: "gray" },
  danger: { variant: "filled", color: "red.8" },
};
