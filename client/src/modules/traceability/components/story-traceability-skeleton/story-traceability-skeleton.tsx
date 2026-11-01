"use client";

import { DSSkeleton } from "@/components/design-system";
import type { FC } from "react";

export const StoryTraceabilitySkeleton: FC = () => {
  return (
    <div aria-busy="true">
      <DSSkeleton lineCount={6} />
    </div>
  );
};
