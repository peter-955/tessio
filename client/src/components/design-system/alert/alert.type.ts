import type { DSIconName } from "../typing/types/icon.type";

export type DSAlertColor = "info" | "success" | "warning" | "danger";

export interface DSAlertStyle {
  icon: DSIconName;
  mantineColor: string;
  textColor: string | undefined;
}

export type DSAlertCloseControl =
  { onClose: () => void; closeLabel: string } | { onClose?: never; closeLabel?: never };
