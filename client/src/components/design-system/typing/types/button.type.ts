import type { ButtonVariant } from "@mantine/core";

export type DSButtonType = "primary" | "default" | "outline" | "ghost" | "danger";

export type DSButtonSize = "sm" | "md";

export interface DSButtonStyle {
  variant: ButtonVariant;
  color?: string;
}
