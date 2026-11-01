import type { MantineColorScheme } from "@mantine/core";

export const isColorScheme = (value: string): value is MantineColorScheme => {
  return value === "light" || value === "dark" || value === "auto";
};
