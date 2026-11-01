"use client";

import { useCallback } from "react";
import type { ColorScheme } from "../typing/types/color-scheme.type";
import { usePatchMe } from "./mutations/use-patch-me";

export const useSaveColorScheme = (): ((colorScheme: ColorScheme) => void) => {
  const { mutate: patchMe } = usePatchMe();

  return useCallback(
    (colorScheme: ColorScheme): void => {
      patchMe({ colorScheme });
    },
    [patchMe],
  );
};
