import { Badge } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DS_BADGE_TEXT_COLORS } from "../typing/constants/badge.constant";
import type { DSBadgeColor } from "../typing/types/badge.type";

interface Props {
  children: ReactNode;
  color?: DSBadgeColor;
  hasDot?: boolean;
}

export const DSBadge: FC<Props> = ({ children, color = "gray", hasDot = false }) => {
  return (
    <Badge
      component="span"
      color={color}
      variant={hasDot ? "dot" : "light"}
      c={hasDot ? undefined : DS_BADGE_TEXT_COLORS[color]}
    >
      {children}
    </Badge>
  );
};
