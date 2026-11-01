"use client";

import { Tooltip } from "@mantine/core";
import type { FC, ReactElement, ReactNode } from "react";
import { DS_TOOLTIP_EVENTS, DS_TOOLTIP_OPEN_DELAY } from "./tooltip.constant";
import type { DSTooltipPosition } from "./tooltip.type";

interface Props {
  label: ReactNode;
  children: ReactElement;
  position?: DSTooltipPosition;
  isDisabled?: boolean;
}

export const DSTooltip: FC<Props> = ({ label, children, position = "top", isDisabled = false }) => {
  return (
    <Tooltip
      label={label}
      position={position}
      disabled={isDisabled}
      openDelay={DS_TOOLTIP_OPEN_DELAY}
      events={DS_TOOLTIP_EVENTS}
      withArrow
    >
      {children}
    </Tooltip>
  );
};
