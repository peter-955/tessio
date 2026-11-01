"use client";

import { Menu } from "@mantine/core";
import Link from "next/link";
import type { FC, ReactElement } from "react";
import { DSIcon } from "../icon/icon";
import styles from "./menu.module.scss";
import type { DSMenuItem, DSMenuPosition } from "./menu.type";

interface Props {
  target: ReactElement;
  items: DSMenuItem[];
  position?: DSMenuPosition;
  width?: number;
}

export const DSMenu: FC<Props> = ({ target, items, position = "bottom-end", width }) => {
  return (
    <Menu position={position} width={width} shadow="md" withInitialFocusPlaceholder={false}>
      <Menu.Target>{target}</Menu.Target>
      <Menu.Dropdown>
        {items.map((item) => {
          if (item.type === "divider") {
            return <Menu.Divider key={item.key} />;
          }
          if (item.type === "label") {
            return <Menu.Label key={item.key}>{item.label}</Menu.Label>;
          }
          const leftSection = item.icon ? <DSIcon name={item.icon} size={16} /> : undefined;
          const color = item.isDanger ? "red" : undefined;
          const className = item.isDanger ? styles.danger : undefined;
          const ariaCurrent = item.isCurrent ? "true" : undefined;
          if (item.href) {
            return (
              <Menu.Item
                key={item.key}
                component={Link}
                href={item.href}
                leftSection={leftSection}
                color={color}
                className={className}
                disabled={item.isDisabled}
                aria-current={ariaCurrent}
                onClick={item.onClick}
              >
                {item.label}
              </Menu.Item>
            );
          }
          return (
            <Menu.Item
              key={item.key}
              leftSection={leftSection}
              color={color}
              className={className}
              disabled={item.isDisabled}
              aria-current={ariaCurrent}
              onClick={item.onClick}
            >
              {item.label}
            </Menu.Item>
          );
        })}
      </Menu.Dropdown>
    </Menu>
  );
};
