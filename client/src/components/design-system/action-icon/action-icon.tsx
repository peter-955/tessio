"use client";

import { ActionIcon } from "@mantine/core";
import type { FC, Ref } from "react";
import { DSIcon } from "../icon/icon";
import { DSTooltip } from "../tooltip/tooltip";
import { DS_BUTTON_STYLES } from "../typing/constants/button.constant";
import type { DSIconName } from "../typing/types/icon.type";
import { DS_ACTION_ICON_SIZES } from "./action-icon.constant";
import type {
  DSActionIconSize,
  DSActionIconTriggerProps,
  DSActionIconType,
} from "./action-icon.type";

interface Props extends DSActionIconTriggerProps {
  icon: DSIconName;
  ariaLabel: string;
  type?: DSActionIconType;
  size?: DSActionIconSize;
  isLoading?: boolean;
  isDisabled?: boolean;
  tooltip?: string;
  hasTooltip?: boolean;
  onClick?: () => void;
  ref?: Ref<HTMLButtonElement>;
}

export const DSActionIcon: FC<Props> = ({
  icon,
  ariaLabel,
  type = "ghost",
  size = "sm",
  isLoading = false,
  isDisabled = false,
  tooltip,
  hasTooltip = false,
  onClick,
  ref,
  ...triggerProps
}) => {
  const { variant, color } = DS_BUTTON_STYLES[type];
  const { control, icon: iconSize } = DS_ACTION_ICON_SIZES[size];
  const button = (
    <ActionIcon
      {...triggerProps}
      ref={ref}
      variant={variant}
      color={color}
      size={control}
      loading={isLoading}
      disabled={isDisabled}
      aria-label={ariaLabel}
      type="button"
      onClick={onClick}
    >
      <DSIcon name={icon} size={iconSize} />
    </ActionIcon>
  );

  if (!hasTooltip && tooltip === undefined) {
    return button;
  }

  return <DSTooltip label={tooltip ?? ariaLabel}>{button}</DSTooltip>;
};
