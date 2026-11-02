import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { LABEL_BADGE_COLORS } from "../../typing/constants/label.constant";
import type { LabelColor } from "../../typing/types/label.type";

interface Props {
  name: string;
  color: LabelColor;
}

export const LabelChip: FC<Props> = ({ name, color }) => {
  return <DSBadge color={LABEL_BADGE_COLORS[color]}>{name}</DSBadge>;
};
