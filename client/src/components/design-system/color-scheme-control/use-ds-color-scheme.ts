"use client";

import type { MantineColorScheme } from "@mantine/core";
import { useMantineColorScheme } from "@mantine/core";

export const useDSColorScheme = (): {
  colorScheme: MantineColorScheme;
  setColorScheme: (value: MantineColorScheme) => void;
} => {
  const { colorScheme, setColorScheme } = useMantineColorScheme();
  return { colorScheme, setColorScheme };
};
