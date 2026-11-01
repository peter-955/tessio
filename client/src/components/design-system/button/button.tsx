import { Button } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DSIcon } from "../icon/icon";
import { DS_BUTTON_STYLES } from "../typing/constants/button.constant";
import type { DSButtonSize, DSButtonType } from "../typing/types/button.type";
import type { DSIconName } from "../typing/types/icon.type";

interface Props {
  children: ReactNode;
  type?: DSButtonType;
  size?: DSButtonSize;
  icon?: DSIconName;
  hasArrow?: boolean;
  isLoading?: boolean;
  isDisabled?: boolean;
  isFullWidth?: boolean;
  isAutoFocused?: boolean;
  nativeType?: "button" | "submit" | "reset";
  formId?: string;
  title?: string;
  ariaExpanded?: boolean;
  ariaControls?: string;
  ariaHasPopup?: "menu" | "dialog" | "listbox";
  ariaLabel?: string;
  onClick?: () => void;
}

export const DSButton: FC<Props> = ({
  children,
  type = "outline",
  size = "sm",
  icon,
  hasArrow = false,
  isLoading = false,
  isDisabled = false,
  isFullWidth = false,
  isAutoFocused = false,
  nativeType = "button",
  formId,
  title,
  ariaExpanded,
  ariaControls,
  ariaHasPopup,
  ariaLabel,
  onClick,
}) => {
  const { variant, color } = DS_BUTTON_STYLES[type];

  return (
    <Button
      variant={variant}
      color={color}
      size={size}
      leftSection={icon ? <DSIcon name={icon} size={16} /> : undefined}
      rightSection={hasArrow ? <DSIcon name="arrowRight" size={16} /> : undefined}
      loading={isLoading}
      disabled={isDisabled}
      fullWidth={isFullWidth}
      autoFocus={isAutoFocused}
      type={nativeType}
      form={formId}
      title={title}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      aria-haspopup={ariaHasPopup}
      aria-label={ariaLabel}
      onClick={onClick}
    >
      {children}
    </Button>
  );
};
