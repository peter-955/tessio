import { Progress } from "@mantine/core";
import type { FC } from "react";
import type { DSProgressSection } from "../typing/types/progress.type";

interface Props {
  label: string;
  sections: DSProgressSection[];
  size?: "sm" | "md" | "lg";
}

export const DSProgress: FC<Props> = ({ label, sections, size = "md" }) => {
  return (
    <Progress.Root size={size} radius="xl" aria-label={label} role="group">
      {sections
        .filter((section) => {
          return section.value > 0;
        })
        .map((section) => {
          return (
            <Progress.Section
              key={section.key}
              value={section.value}
              color={section.color}
              aria-label={section.label}
            />
          );
        })}
    </Progress.Root>
  );
};
