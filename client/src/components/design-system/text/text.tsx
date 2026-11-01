import { Text } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DS_TEXT_COLORS, DS_TEXT_WEIGHTS } from "../typing/constants/text.constant";
import type {
  DSTextColor,
  DSTextElement,
  DSTextSize,
  DSTextWeight,
} from "../typing/types/text.type";

interface Props {
  children: ReactNode;
  size?: DSTextSize;
  color?: DSTextColor;
  weight?: DSTextWeight;
  component?: DSTextElement;
  className?: string;
  id?: string;
}

export const DSText: FC<Props> = ({
  children,
  size,
  color = "default",
  weight = "regular",
  component = "p",
  className,
  id,
}) => {
  return (
    <Text
      component={component}
      size={size}
      c={DS_TEXT_COLORS[color]}
      fw={DS_TEXT_WEIGHTS[weight]}
      className={className}
      id={id}
    >
      {children}
    </Text>
  );
};
