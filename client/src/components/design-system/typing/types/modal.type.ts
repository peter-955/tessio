import type { DSIconName } from "./icon.type";

export interface DSModalAction {
  label: string;
  icon?: DSIconName;
  type?: "primary" | "danger";
  isLoading?: boolean;
  isDisabled?: boolean;
  isAutoFocused?: boolean;
  formId?: string;
  onClick?: () => void;
}
