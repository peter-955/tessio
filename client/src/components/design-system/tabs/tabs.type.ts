import type { DSIconName } from "../typing/types/icon.type";

export interface DSTabItem<T extends string> {
  value: T;
  label: string;
  icon?: DSIconName;
  count?: number;
  isDisabled?: boolean;
}
