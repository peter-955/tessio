import type { FC } from "react";
import { DS_ICONS, DS_ICON_STROKE } from "../typing/constants/icon.constant";
import type { DSIconName } from "../typing/types/icon.type";

interface Props {
  name: DSIconName;
  size?: number;
  className?: string;
}

export const DSIcon: FC<Props> = ({ name, size = 18, className }) => {
  const IconComponent = DS_ICONS[name];

  return <IconComponent size={size} stroke={DS_ICON_STROKE} className={className} aria-hidden />;
};
