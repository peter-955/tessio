import { Button } from "@mantine/core";
import Link from "next/link";
import type { FC, ReactNode } from "react";
import { DSIcon } from "../icon/icon";
import { DS_BUTTON_STYLES } from "../typing/constants/button.constant";
import type { DSButtonSize, DSButtonType } from "../typing/types/button.type";
import type { DSIconName } from "../typing/types/icon.type";

interface Props {
  href: string;
  children: ReactNode;
  type?: DSButtonType;
  size?: DSButtonSize;
  icon?: DSIconName;
  hasArrow?: boolean;
  isExternal?: boolean;
  isFullWidth?: boolean;
}

export const DSButtonLink: FC<Props> = ({
  href,
  children,
  type = "outline",
  size = "sm",
  icon,
  hasArrow = false,
  isExternal = false,
  isFullWidth = false,
}) => {
  const { variant, color } = DS_BUTTON_STYLES[type];
  const leftSection = icon ? <DSIcon name={icon} size={16} /> : undefined;
  const rightSection = hasArrow ? <DSIcon name="arrowRight" size={16} /> : undefined;

  if (isExternal) {
    return (
      <Button
        component="a"
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        variant={variant}
        color={color}
        size={size}
        leftSection={leftSection}
        rightSection={rightSection}
        fullWidth={isFullWidth}
      >
        {children}
      </Button>
    );
  }

  return (
    <Button
      component={Link}
      href={href}
      variant={variant}
      color={color}
      size={size}
      leftSection={leftSection}
      rightSection={rightSection}
      fullWidth={isFullWidth}
    >
      {children}
    </Button>
  );
};
