import type { DSIconName } from "../typing/types/icon.type";

export interface DSMenuActionItem {
  key: string;
  type?: "action";
  label: string;
  icon?: DSIconName;
  isDanger?: boolean;
  isDisabled?: boolean;
  isCurrent?: boolean;
  onClick?: () => void;
  href?: string;
}

export interface DSMenuDividerItem {
  key: string;
  type: "divider";
}

export interface DSMenuLabelItem {
  key: string;
  type: "label";
  label: string;
}

export type DSMenuItem = DSMenuActionItem | DSMenuDividerItem | DSMenuLabelItem;

export type DSMenuPosition = "bottom-end" | "bottom-start";
