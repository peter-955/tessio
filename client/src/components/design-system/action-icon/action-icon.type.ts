import type { ButtonHTMLAttributes } from "react";
import type { DSButtonType } from "../typing/types/button.type";

export type DSActionIconType = Exclude<DSButtonType, "primary">;

export type DSActionIconSize = "sm" | "md";

export interface DSActionIconSizeStyle {
  control: "input-sm" | "input-md";
  icon: number;
}

export type DSActionIconTriggerProps = Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  "children" | "className" | "color" | "disabled" | "onClick" | "style" | "type"
>;
