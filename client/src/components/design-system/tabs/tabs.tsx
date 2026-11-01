"use client";

import { Tabs } from "@mantine/core";
import type { ReactElement, ReactNode } from "react";
import { DSBadge } from "../badge/badge";
import { DSIcon } from "../icon/icon";
import type { DSTabItem } from "./tabs.type";

interface Props<T extends string> {
  items: DSTabItem<T>[];
  value: T;
  onChange: (value: T) => void;
  children: ReactNode;
  ariaLabel: string;
}

export const DSTabs = <T extends string>({
  items,
  value,
  onChange,
  children,
  ariaLabel,
}: Props<T>): ReactElement => {
  const handleChange = (nextValue: string | null): void => {
    const selectedItem = items.find((item) => {
      return item.value === nextValue;
    });
    if (selectedItem) {
      onChange(selectedItem.value);
    }
  };

  return (
    <Tabs value={value} onChange={handleChange} keepMounted={false}>
      <Tabs.List aria-label={ariaLabel}>
        {items.map((item) => {
          return (
            <Tabs.Tab
              key={item.value}
              value={item.value}
              disabled={item.isDisabled}
              leftSection={item.icon ? <DSIcon name={item.icon} size={16} /> : undefined}
              rightSection={item.count === undefined ? undefined : <DSBadge>{item.count}</DSBadge>}
            >
              {item.label}
            </Tabs.Tab>
          );
        })}
      </Tabs.List>
      {children}
    </Tabs>
  );
};
